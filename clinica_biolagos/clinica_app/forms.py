from django import forms
from django.core.exceptions import ValidationError
from .models import Paciente, Cita, Medico, BloqueHorario, validar_rut
from .access import get_user_medico, get_user_paciente, paciente_queryset_for_user


# ─── Helper RUT ──────────────────────────────────────────────────────────────
def _clean_rut(rut):
    """Lanza forms.ValidationError si el RUT es inválido según Módulo 11."""
    try:
        validar_rut(rut)
    except ValidationError as e:
        raise forms.ValidationError(e.message)
    return rut


# ─── PacienteForm ─────────────────────────────────────────────────────────────
class PacienteForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha de Nacimiento'
    )

    class Meta:
        model = Paciente
        fields = [
            'nombre', 'apellido', 'rut', 'fecha_nacimiento', 'sexo',
            'email', 'telefono', 'direccion', 'ciudad', 'prevision',
            'alergias', 'observaciones'
        ]
        widgets = {
            'nombre':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'}),
            'apellido':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: González'}),
            'rut':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'sexo':          forms.Select(attrs={'class': 'form-select'}),
            'email':         forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'direccion':     forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad':        forms.TextInput(attrs={'class': 'form-control'}),
            'prevision':     forms.TextInput(attrs={'class': 'form-control'}),
            'alergias':      forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_rut(self):
        return _clean_rut(self.cleaned_data.get('rut', ''))


# ─── MedicoForm ───────────────────────────────────────────────────────────────
class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['nombre', 'apellido', 'rut', 'especialidad', 'email', 'telefono', 'activo']
        widgets = {
            'nombre':       forms.TextInput(attrs={'class': 'form-control'}),
            'apellido':     forms.TextInput(attrs={'class': 'form-control'}),
            'rut':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
            'email':        forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono':     forms.TextInput(attrs={'class': 'form-control'}),
            'activo':       forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_rut(self):
        return _clean_rut(self.cleaned_data.get('rut', ''))


# ─── CitaForm (uso interno: staff/médico) ─────────────────────────────────────
class CitaForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_fecha'}),
        label='Fecha'
    )
    hora = forms.TimeField(
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_hora'}),
        label='Hora'
    )

    class Meta:
        model = Cita
        fields = ['paciente', 'medico', 'fecha', 'hora', 'motivo', 'estado', 'notas']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'medico':   forms.Select(attrs={'class': 'form-select'}),
            'motivo':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivo de la consulta'}),
            'estado':   forms.Select(attrs={'class': 'form-select'}),
            'notas':    forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['hora'].choices = [('', '— Seleccione médico y fecha primero —')]

        if not user or user.is_superuser:
            self._actualizar_hora_choices_from_data()
            return

        medico = get_user_medico(user)
        paciente = get_user_paciente(user)
        if medico:
            self.fields['paciente'].queryset = paciente_queryset_for_user(user)
            self.fields['medico'].queryset = Medico.objects.filter(pk=medico.pk)
            self.fields['medico'].initial = medico
            self._actualizar_hora_choices_from_data()
            return

        if paciente:
            self.fields['paciente'].queryset = Paciente.objects.filter(pk=paciente.pk)
            self.fields['paciente'].initial = paciente
            self.fields['estado'].disabled = True
            self.fields['estado'].required = False
            self.fields['estado'].widget.attrs['class'] = 'form-select disabled'
            self._actualizar_hora_choices_from_data()
            return

        self.fields['estado'].choices = [('pendiente', 'Pendiente')]
        self.fields['estado'].initial = 'pendiente'
        self.fields['paciente'].queryset = paciente_queryset_for_user(user)
        self._actualizar_hora_choices_from_data()

    def _actualizar_hora_choices_from_data(self):
        medico_id = None
        fecha_val = None
        if self.is_bound:
            medico_id = self.data.get('medico')
            fecha_val = self.data.get('fecha')
        else:
            medico = self.initial.get('medico')
            fecha_val = self.initial.get('fecha')
            if medico:
                medico_id = medico.pk if hasattr(medico, 'pk') else medico

        if not medico_id or not fecha_val:
            return

        try:
            from datetime import date
            medico = Medico.objects.get(pk=medico_id, activo=True)
            if isinstance(fecha_val, date):
                fecha = fecha_val
            else:
                fecha = date.fromisoformat(str(fecha_val))
        except (ValueError, Medico.DoesNotExist, TypeError):
            return

        bloques = BloqueHorario.bloques_para_medico_fecha(medico, fecha)
        horas_ocupadas = set(
            Cita.objects.filter(medico=medico, fecha=fecha)
            .exclude(estado='cancelada')
            .values_list('hora', flat=True)
        )
        horas = sorted({
            f'{h.hour:02d}:{h.minute:02d}'
            for bloque in bloques
            for h in bloque.horas_disponibles()
            if h not in horas_ocupadas
        })
        if horas:
            self.fields['hora'].choices = [('', '— Seleccione una hora —')] + [(h, h) for h in horas]
        else:
            self.fields['hora'].choices = [('', '— Sin horas disponibles —')]


# ─── SolicitudHoraForm (formulario público para pacientes) ───────────────────
class SolicitudHoraForm(forms.Form):
    """
    Formulario público de solicitud de hora.
    Las horas disponibles se cargan dinámicamente vía AJAX (endpoint horas_disponibles_json).
    Al validar en servidor se comprueba nuevamente que la hora esté en un bloque
    y que no esté ya reservada.
    """
    nombre = forms.CharField(
        label='Nombre', max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'})
    )
    apellido = forms.CharField(
        label='Apellido', max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: González'})
    )
    rut = forms.CharField(
        label='RUT', max_length=12,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    telefono = forms.CharField(
        label='Teléfono', max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'})
    )
    medico = forms.ModelChoiceField(
        label='Médico',
        queryset=Medico.objects.filter(activo=True).select_related('especialidad'),
        empty_label='— Seleccione un médico —',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_medico'})
    )
    fecha = forms.DateField(
        label='Fecha',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_fecha'})
    )
    hora = forms.ChoiceField(
        label='Hora disponible',
        choices=[('', '— Seleccione médico y fecha primero —')],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_hora'})
    )
    motivo = forms.CharField(
        label='Motivo de la consulta', max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Motivo de la consulta'
        })
    )
    notas = forms.CharField(
        label='Notas adicionales', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user and user.is_authenticated and user.username.lower() == 'yesi':
            carlos = Medico.objects.filter(nombre__iexact='Carlos', apellido__iexact='Munoz').first()
            if carlos:
                self.fields['medico'].queryset = Medico.objects.filter(pk=carlos.pk)
                self.fields['medico'].initial = carlos
                self.fields['medico'].empty_label = None

        medico_id = None
        fecha_val = None
        if self.is_bound:
            medico_id = self.data.get('medico')
            fecha_val = self.data.get('fecha')
        elif self.initial.get('medico'):
            medico_id = self.initial.get('medico').pk if hasattr(self.initial.get('medico'), 'pk') else self.initial.get('medico')
            fecha_val = self.initial.get('fecha')

        if medico_id and fecha_val:
            try:
                medico = Medico.objects.get(pk=medico_id, activo=True)
                from datetime import date
                if isinstance(fecha_val, date):
                    fecha = fecha_val
                else:
                    fecha = date.fromisoformat(str(fecha_val))
                self._actualizar_hora_choices(medico, fecha)
            except (ValueError, Medico.DoesNotExist):
                self.fields['hora'].choices = [('', '— Seleccione médico y fecha primero —')]

    def _actualizar_hora_choices(self, medico, fecha):
        bloques = BloqueHorario.bloques_para_medico_fecha(medico, fecha)
        horas_ocupadas = set(
            Cita.objects.filter(medico=medico, fecha=fecha)
            .exclude(estado='cancelada')
            .values_list('hora', flat=True)
        )
        horas = sorted({
            f'{h.hour:02d}:{h.minute:02d}'
            for bloque in bloques
            for h in bloque.horas_disponibles()
            if h not in horas_ocupadas
        })
        if horas:
            choices = [('', '— Seleccione una hora —')] + [(h, h) for h in horas]
        else:
            choices = [('', '— Sin horas disponibles —')]
        self.fields['hora'].choices = choices

    def clean_rut(self):
        return _clean_rut(self.cleaned_data.get('rut', ''))

    def clean(self):
        cleaned = super().clean()
        medico = cleaned.get('medico')
        fecha  = cleaned.get('fecha')
        hora_s = cleaned.get('hora', '').strip()

        if self.user and self.user.is_authenticated and self.user.username.lower() == 'yesi':
            carlos = Medico.objects.filter(nombre__iexact='Carlos', apellido__iexact='Munoz').first()
            if not carlos:
                raise forms.ValidationError('No se encontró el médico asignado para su solicitud.')
            if medico and medico != carlos:
                raise forms.ValidationError('Solo puede reservar con el médico Carlos.')

        if not (medico and fecha and hora_s):
            return cleaned

        # --- Parsear hora ---
        from datetime import time as dt_time
        try:
            h, m = hora_s.split(':')
            hora_obj = dt_time(int(h), int(m))
        except (ValueError, AttributeError):
            raise forms.ValidationError('Hora seleccionada inválida.')

        # --- Verificar que la hora esté en un bloque disponible ---
        bloques = BloqueHorario.bloques_para_medico_fecha(medico, fecha)
        if not bloques.exists():
            raise forms.ValidationError(
                'El médico seleccionado no tiene horario definido para esa fecha.'
            )
        horas_validas = []
        for b in bloques:
            horas_validas.extend(b.horas_disponibles())

        if hora_obj not in horas_validas:
            raise forms.ValidationError(
                'La hora seleccionada no corresponde a un horario disponible del médico.'
            )

        # --- Verificar que no esté ya reservada ---
        if Cita.objects.filter(
            medico=medico, fecha=fecha, hora=hora_obj
        ).exclude(estado='cancelada').exists():
            raise forms.ValidationError(
                'Esa hora ya está reservada. Por favor seleccione otra.'
            )

        cleaned['hora_obj'] = hora_obj
        return cleaned


# ─── BloqueHorarioForm ────────────────────────────────────────────────────────
class BloqueHorarioForm(forms.ModelForm):
    todos_los_dias = forms.BooleanField(
        required=False,
        label='Todos los días',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Marca esto para que el bloque se aplique todos los días de la semana.'
    )

    class Meta:
        model = BloqueHorario
        fields = ['medico', 'fecha', 'dia_semana', 'hora_inicio', 'hora_fin']
        widgets = {
            'medico':      forms.Select(attrs={'class': 'form-select'}),
            'fecha':       forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dia_semana':  forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin':    forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
        help_texts = {
            'fecha':      'Opcional. Si se define, el bloque aplica sólo ese día concreto.',
            'dia_semana': 'Define un bloque recurrente semanal por el día de la semana. Dejar vacío si marca "Todos los días".',
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.user and not self.user.is_superuser:
            medico = get_user_medico(self.user)
            if medico:
                self.fields['medico'].queryset = Medico.objects.filter(pk=medico.pk)
                self.fields['medico'].initial = medico
                self.fields['medico'].disabled = True
        if self.instance and self.instance.pk:
            if self.instance.fecha is None and self.instance.dia_semana is None:
                self.fields['todos_los_dias'].initial = True

    def clean(self):
        cleaned = super().clean()
        fecha      = cleaned.get('fecha')
        dia_semana = cleaned.get('dia_semana')
        hi         = cleaned.get('hora_inicio')
        hf         = cleaned.get('hora_fin')

        todos_los_dias = cleaned.get('todos_los_dias')
        if todos_los_dias:
            if fecha or dia_semana is not None:
                raise forms.ValidationError(
                    'Marque "Todos los días" y deje vacíos Fecha y Día de la semana.'
                )
            cleaned['fecha'] = None
            cleaned['dia_semana'] = None
            return cleaned

        if not fecha and dia_semana is None:
            raise forms.ValidationError(
                'Debe indicar una Fecha específica, un Día de la semana o Todos los días.'
            )
        if fecha and dia_semana is not None:
            raise forms.ValidationError(
                'Indique Fecha específica O Día de la semana, no ambos a la vez.'
            )
        if hi and hf and hi >= hf:
            raise forms.ValidationError(
                'La hora de inicio debe ser anterior a la hora de fin.'
            )
        return cleaned
