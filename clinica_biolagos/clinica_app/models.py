from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validar_rut(rut):
    """
    Valida un RUT chileno usando el algoritmo Módulo 11.
    Acepta formatos: 12345678-9  /  12.345.678-9  /  123456789
    """
    rut = rut.strip().upper().replace('.', '').replace('-', '')
    if len(rut) < 2:
        raise ValidationError('RUT inválido: demasiado corto.')
    cuerpo = rut[:-1]
    dv = rut[-1]
    if not cuerpo.isdigit():
        raise ValidationError('RUT inválido: el cuerpo debe contener sólo dígitos.')
    # Cálculo Módulo 11
    suma = 0
    factor = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        dv_esperado = '0'
    elif resto == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(resto)
    if dv != dv_esperado:
        raise ValidationError(
            f'RUT inválido: dígito verificador incorrecto (esperado: {dv_esperado}).'
        )


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut])
    especialidad = models.ForeignKey(
        Especialidad, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='medicos'
    )
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"Dr(a). {self.apellido}, {self.nombre}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Paciente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut])
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='O')
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200, blank=True)
    ciudad = models.CharField(max_length=100, blank=True, default='Puerto Montt')
    prevision = models.CharField(max_length=100, blank=True, default='Fonasa')
    alergias = models.TextField(blank=True, help_text='Alergias conocidas del paciente')
    observaciones = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pacientes_creados'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.rut})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Cita(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='citas'
    )
    medico = models.ForeignKey(
        Medico, on_delete=models.CASCADE, related_name='citas'
    )
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=300)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='citas_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f"Cita {self.paciente} con {self.medico} - {self.fecha}"

    def clean(self):
        if self.medico and self.fecha and self.hora:
            bloques = BloqueHorario.bloques_para_medico_fecha(self.medico, self.fecha)
            if not bloques.exists():
                raise ValidationError(
                    'No existe un bloque de horario definido para ese médico en la fecha seleccionada.'
                )
            horas_validas = {h for bloque in bloques for h in bloque.horas_disponibles()}
            if self.hora not in horas_validas:
                raise ValidationError(
                    'La hora no está dentro del bloque horario disponible del médico.'
                )


class BloqueHorario(models.Model):
    """
    Bloque de disponibilidad de un médico.
    Versión simple: el bloque es el mismo todos los días (dia_semana=None, fecha=None).
    Versión avanzada: el bloque se repite por día de la semana (dia_semana definido).
    Opcional: puede definirse un bloque para una fecha específica con 'fecha'.
    Si 'fecha' está definida, ese bloque tiene prioridad sobre los recurrentes.
    """
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    medico = models.ForeignKey(
        Medico, on_delete=models.CASCADE, related_name='bloques_horarios',
        verbose_name='Médico'
    )
    # Fecha específica: bloque para un día concreto (disponibilidad especial)
    fecha = models.DateField(
        null=True, blank=True, verbose_name='Fecha específica',
        help_text='Opcional. Define un bloque válido solo para ese día concreto.'
    )
    # Día de la semana: bloque recurrente semanal por día de la semana
    dia_semana = models.IntegerField(
        choices=DIAS_SEMANA, null=True, blank=True, verbose_name='Día de la semana',
        help_text='Opcional. Define un bloque que se repite semanalmente en el día seleccionado.'
    )
    hora_inicio = models.TimeField(verbose_name='Hora inicio')
    hora_fin = models.TimeField(verbose_name='Hora fin')

    class Meta:
        verbose_name = 'Bloque Horario'
        verbose_name_plural = 'Bloques Horarios'
        ordering = ['medico', 'dia_semana', 'fecha', 'hora_inicio']

    def __str__(self):
        if self.fecha:
            return (
                f"{self.medico.nombre_completo} — "
                f"{self.fecha.strftime('%d/%m/%Y')} "
                f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')}"
            )
        if self.dia_semana is None:
            return (
                f"{self.medico.nombre_completo} — "
                f"Todos los días "
                f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')}"
            )
        dia = dict(self.DIAS_SEMANA).get(self.dia_semana, '?')
        return (
            f"{self.medico.nombre_completo} — "
            f"{dia} "
            f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')}"
        )

    def clean(self):
        if self.fecha and self.dia_semana is not None:
            raise ValidationError(
                'Indique Fecha específica, Día de la semana o Todos los días, no combinaciones.'
            )
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')

    def horas_disponibles(self, intervalo_minutos=30):
        """
        Retorna lista de objetos time con todas las horas dentro del bloque,
        separadas por intervalo_minutos.
        """
        from datetime import datetime, timedelta, date
        ref = self.fecha if self.fecha else date.today()
        horas = []
        actual = datetime.combine(ref, self.hora_inicio)
        fin = datetime.combine(ref, self.hora_fin)
        while actual < fin:
            horas.append(actual.time())
            actual += timedelta(minutes=intervalo_minutos)
        return horas

    @classmethod
    def bloques_para_medico_fecha(cls, medico, fecha):
        """
        Retorna los bloques que aplican a un médico en una fecha concreta.
        Prioridad:
          1. Bloques con fecha específica == fecha
          2. Bloques con dia_semana == fecha.weekday() (si no hay bloques específicos)
        """
        especificos = cls.objects.filter(medico=medico, fecha=fecha)
        if especificos.exists():
            return especificos
        return cls.objects.filter(
            medico=medico,
            fecha__isnull=True
        ).filter(
            models.Q(dia_semana=fecha.weekday()) | models.Q(dia_semana__isnull=True)
        )
