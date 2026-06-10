from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.utils import timezone

from .models import Paciente, Cita, Medico, BloqueHorario
from .forms import (
    PacienteForm, CitaForm, MedicoForm,
    SolicitudHoraForm, BloqueHorarioForm
)
from .access import (
    can_access_cita,
    can_access_paciente,
    cita_queryset_for_user,
    get_user_medico,
    is_medico_user,
    is_paciente_user,
    paciente_queryset_for_user,
)


# ============================================================
#  PACIENTES
# ============================================================

@login_required
def paciente_lista(request):
    q = request.GET.get('q', '')
    pacientes = paciente_queryset_for_user(request.user).order_by('apellido', 'nombre')
    if q:
        pacientes = (
            pacientes.filter(apellido__icontains=q) |
            pacientes.filter(nombre__icontains=q) |
            pacientes.filter(rut__icontains=q)
        ).distinct()
    return render(request, 'clinica_app/paciente_lista.html', {
        'pacientes': pacientes, 'q': q
    })


@login_required
def paciente_crear(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.creado_por = request.user
            paciente.save()
            messages.success(request, f'Paciente {paciente.nombre_completo} registrado correctamente.')
            return redirect('clinica:paciente_lista')
    else:
        form = PacienteForm()
    return render(request, 'clinica_app/paciente_form.html', {
        'form': form, 'titulo': 'Nuevo Paciente'
    })


@login_required
def paciente_detalle(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if not can_access_paciente(request.user, paciente):
        raise PermissionDenied
    citas = cita_queryset_for_user(request.user).filter(paciente=paciente).order_by('-fecha', '-hora')
    return render(request, 'clinica_app/paciente_detalle.html', {
        'paciente': paciente,
        'citas': citas,
        'can_manage_citas': request.user.is_superuser or is_medico_user(request.user),
    })


@login_required
def paciente_editar(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if not can_access_paciente(request.user, paciente):
        raise PermissionDenied
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Paciente {paciente.nombre_completo} actualizado.')
            return redirect('clinica:paciente_detalle', pk=pk)
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'clinica_app/paciente_form.html', {
        'form': form,
        'titulo': f'Editar Paciente: {paciente.nombre_completo}',
        'paciente': paciente
    })


@login_required
def paciente_eliminar(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        nombre = paciente.nombre_completo
        paciente.delete()
        messages.success(request, f'Paciente {nombre} eliminado.')
        return redirect('clinica:paciente_lista')
    return render(request, 'clinica_app/confirmar_eliminar.html', {
        'objeto': paciente,
        'tipo': 'paciente',
        'url_cancelar': 'clinica:paciente_lista'
    })


# ============================================================
#  CITAS
# ============================================================

def solicitar_hora(request):
    """Vista pública: el paciente solicita una hora."""
    if request.method == 'POST':
        form = SolicitudHoraForm(request.POST, user=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            rut = cd['rut']
            paciente, created = Paciente.objects.get_or_create(
                rut=rut,
                defaults={
                    'nombre': cd['nombre'],
                    'apellido': cd['apellido'],
                    'fecha_nacimiento': timezone.localdate(),
                    'sexo': 'O',
                    'email': cd['email'],
                    'telefono': cd['telefono'],
                    'creado_por': request.user if request.user.is_authenticated else None,
                }
            )
            if not created:
                paciente.nombre   = cd['nombre']
                paciente.apellido = cd['apellido']
                paciente.email    = cd['email']
                paciente.telefono = cd['telefono']
                paciente.save()

            # hora_obj viene ya parseado en el clean del formulario
            hora = cd.get('hora_obj') or cd['hora']

            cita = Cita(
                paciente=paciente,
                medico=cd['medico'],
                fecha=cd['fecha'],
                hora=hora,
                motivo=cd['motivo'],
                notas=cd.get('notas', ''),
                estado='pendiente',
                creado_por=request.user if request.user.is_authenticated else None,
            )
            try:
                cita.full_clean()
            except ValidationError as e:
                form.add_error(None, e)
                return render(request, 'clinica_app/solicitar_hora.html', {'form': form})
            cita.save()
            messages.success(
                request,
                'Solicitud de hora enviada correctamente. Quedará en estado pendiente hasta su confirmación.'
            )
            return redirect('home')
    else:
        form = SolicitudHoraForm(user=request.user)
    return render(request, 'clinica_app/solicitar_hora.html', {'form': form})


@login_required
def cita_lista(request):
    estado = request.GET.get('estado', '')
    citas = cita_queryset_for_user(request.user).order_by('-fecha', '-hora')
    if estado:
        citas = citas.filter(estado=estado)
    return render(request, 'clinica_app/cita_lista.html', {
        'citas': citas,
        'estado': estado,
        'estados': Cita.ESTADO_CHOICES,
        'can_manage_citas': request.user.is_superuser or is_medico_user(request.user) or is_paciente_user(request.user),
        'can_delete_citas': request.user.is_superuser or is_medico_user(request.user) or is_paciente_user(request.user),
    })


@login_required
def cita_crear(request):
    if request.method == 'POST':
        form = CitaForm(request.POST, user=request.user)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.creado_por = request.user
            if not request.user.is_superuser and not is_medico_user(request.user):
                cita.estado = 'pendiente' # Forzar estado para pacientes
            cita.save()
            messages.success(request, 'Cita agendada correctamente.')
            return redirect('clinica:cita_lista')
    else:
        form = CitaForm(user=request.user)
    return render(request, 'clinica_app/cita_form.html', {
        'form': form, 'titulo': 'Nueva Cita'
    })


@login_required
def cita_detalle(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if not can_access_cita(request.user, cita):
        raise PermissionDenied
    return render(request, 'clinica_app/cita_detalle.html', {
        'cita': cita,
        'can_manage_citas': request.user.is_superuser or is_medico_user(request.user) or is_paciente_user(request.user),
        'can_delete_citas': request.user.is_superuser or is_medico_user(request.user) or is_paciente_user(request.user),
    })


@login_required
def cita_editar(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if not can_access_cita(request.user, cita):
        raise PermissionDenied
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada correctamente.')
            return redirect('clinica:cita_detalle', pk=pk)
    else:
        form = CitaForm(instance=cita, user=request.user)
    return render(request, 'clinica_app/cita_form.html', {
        'form': form, 'titulo': 'Editar Cita', 'cita': cita
    })


@login_required
def cita_eliminar(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if not can_access_cita(request.user, cita):
        raise PermissionDenied
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada.')
        return redirect('clinica:cita_lista')
    return render(request, 'clinica_app/confirmar_eliminar.html', {
        'objeto': cita,
        'tipo': 'cita',
        'url_cancelar': 'clinica:cita_lista'
    })


# ============================================================
#  MÉDICOS
# ============================================================

@login_required
def medico_lista(request):
    medicos = Medico.objects.select_related('especialidad').order_by('apellido', 'nombre')
    return render(request, 'clinica_app/medico_lista.html', {'medicos': medicos})


@login_required
def medico_crear(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            medico = form.save()
            messages.success(request, f'Dr(a). {medico.nombre_completo} registrado.')
            return redirect('clinica:medico_lista')
    else:
        form = MedicoForm()
    return render(request, 'clinica_app/medico_form.html', {
        'form': form, 'titulo': 'Nuevo Médico'
    })


@login_required
def medico_editar(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    medico = get_object_or_404(Medico, pk=pk)
    if request.method == 'POST':
        form = MedicoForm(request.POST, instance=medico)
        if form.is_valid():
            form.save()
            messages.success(request, f'Médico {medico.nombre_completo} actualizado.')
            return redirect('clinica:medico_lista')
    else:
        form = MedicoForm(instance=medico)
    return render(request, 'clinica_app/medico_form.html', {
        'form': form,
        'titulo': f'Editar: Dr(a). {medico.nombre_completo}',
        'medico': medico
    })


@login_required
def medico_eliminar(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    medico = get_object_or_404(Medico, pk=pk)
    if request.method == 'POST':
        nombre = medico.nombre_completo
        medico.delete()
        messages.success(request, f'Médico {nombre} eliminado.')
        return redirect('clinica:medico_lista')
    return render(request, 'clinica_app/confirmar_eliminar.html', {
        'objeto': medico,
        'tipo': 'médico',
        'url_cancelar': 'clinica:medico_lista'
    })


# ============================================================
#  BLOQUES HORARIOS
# ============================================================

@login_required
def bloque_lista(request, medico_pk=None):
    """
    Lista y gestión de bloques horarios.
    - Superuser ve todos los bloques.
    - Médicos solo ven y gestionan sus propios bloques.
    - Solo superuser puede gestionar bloques.
    """
    user_medico = get_user_medico(request.user)
    medicos = []
    medico_sel = None

    if request.user.is_superuser:
        medicos = Medico.objects.filter(activo=True).order_by('apellido', 'nombre')
        if medico_pk:
            medico_sel = get_object_or_404(Medico, pk=medico_pk)
    else:
        if not user_medico:
            raise PermissionDenied
        if medico_pk and int(medico_pk) != user_medico.pk:
            raise PermissionDenied
        medico_sel = user_medico

    bloques_qs = BloqueHorario.objects.select_related('medico').order_by(
        'medico__apellido', 'dia_semana', 'fecha', 'hora_inicio'
    )

    if not request.user.is_superuser:
        bloques_qs = bloques_qs.filter(medico=user_medico)
    elif medico_sel:
        bloques_qs = bloques_qs.filter(medico=medico_sel)

    if request.method == 'POST':
        form = BloqueHorarioForm(request.POST, user=request.user)
        if form.is_valid():
            bloque = form.save(commit=False)
            bloque.save()
            messages.success(request, f'Bloque horario creado: {bloque}')
            return redirect('clinica:bloque_lista')
    else:
        initial = {}
        if medico_sel:
            initial['medico'] = medico_sel
        form = BloqueHorarioForm(initial=initial, user=request.user)

    return render(request, 'clinica_app/bloque_horario_lista.html', {
        'titulo_seccion': "Gestión de Bloques Horarios" if request.user.is_superuser else "Mis Bloques Horarios",
        'form': form if not is_paciente_user(request.user) else None,
        'bloques': bloques_qs,
        'medicos': medicos,
        'medico_sel': medico_sel,
        'user_medico': user_medico,
    })


@login_required
def bloque_editar(request, pk):
    bloque = get_object_or_404(BloqueHorario, pk=pk)
    if not can_access_bloque(request.user, bloque):
        raise PermissionDenied
    if request.method == 'POST':
        form = BloqueHorarioForm(request.POST, instance=bloque, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Bloque horario actualizado: {bloque}')
            return redirect('clinica:bloque_lista')
    else:
        form = BloqueHorarioForm(instance=bloque, user=request.user)
    return render(request, 'clinica_app/bloque_horario_form.html', {
        'form': form,
        'titulo': f'Editar Bloque: {bloque}',
        'bloque': bloque,
    })


@login_required
def bloque_eliminar(request, pk):
    bloque = get_object_or_404(BloqueHorario, pk=pk)
    if not can_access_bloque(request.user, bloque):
        raise PermissionDenied
    if request.method == 'POST':
        bloque.delete()
        messages.success(request, 'Bloque horario eliminado.')
        return redirect('clinica:bloque_lista')
    return render(request, 'clinica_app/confirmar_eliminar.html', {
        'objeto': bloque,
        'tipo': 'bloque horario',
        'url_cancelar': 'clinica:bloque_lista'
    })


# ============================================================
#  API JSON — horas disponibles
# ============================================================

def horas_disponibles_json(request):
    """
    GET /api/horas-disponibles/?medico=<id>&fecha=<YYYY-MM-DD>
    Retorna JSON con las horas disponibles (en bloques) que no han sido reservadas.
    Soporta bloques recurrentes (dia_semana) y bloques por fecha específica.
    """
    medico_id = request.GET.get('medico', '').strip()
    fecha_str = request.GET.get('fecha', '').strip()

    if not medico_id or not fecha_str:
        return JsonResponse({'horas': []})

    try:
        from datetime import date
        fecha = date.fromisoformat(fecha_str)
        medico = Medico.objects.get(pk=medico_id, activo=True)
    except (ValueError, Medico.DoesNotExist):
        return JsonResponse({'horas': [], 'error': 'Médico o fecha inválidos.'})

    # Obtener bloques que aplican a esa fecha
    bloques = BloqueHorario.bloques_para_medico_fecha(medico, fecha)

    # Horas ya reservadas (excluir canceladas)
    horas_ocupadas = set(
        Cita.objects.filter(medico=medico, fecha=fecha)
        .exclude(estado='cancelada')
        .values_list('hora', flat=True)
    )

    horas = []
    for bloque in bloques:
        for h in bloque.horas_disponibles():
            if h not in horas_ocupadas:
                horas.append(f'{h.hour:02d}:{h.minute:02d}')

    # Eliminar duplicados y ordenar
    horas = sorted(set(horas))
    return JsonResponse({'horas': horas})
