from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from clinica_app.models import Paciente, Cita, Medico
from clinica_app.access import cita_queryset_for_user, get_user_medico


def home(request):
    """Vista pública – página de inicio."""
    medicos = Medico.objects.all()[:4]
    return render(request, 'core/home.html', {'medicos': medicos})


def nosotros(request):
    """Vista pública – quiénes somos."""
    return render(request, 'core/nosotros.html')


def servicios(request):
    """Vista pública – servicios de la clínica."""
    return render(request, 'core/servicios.html')


def contacto(request):
    """Vista pública – formulario de contacto."""
    if request.method == 'POST':
        messages.success(request, 'Mensaje enviado correctamente. Nos pondremos en contacto pronto.')
        return redirect('contacto')
    return render(request, 'core/contacto.html')


@login_required
def dashboard(request):
    """Vista privada – panel de control del staff."""
    total_pacientes = Paciente.objects.count()
    total_citas = Cita.objects.count()
    citas_pendientes = Cita.objects.filter(estado='pendiente').count()
    citas_hoy = Cita.objects.filter(estado='confirmada').count()
    ultimas_citas = cita_queryset_for_user(request.user).order_by('-fecha', '-hora')[:5]
    medico_usuario = get_user_medico(request.user)

    context = {
        'total_pacientes': total_pacientes,
        'total_citas': total_citas,
        'citas_pendientes': citas_pendientes,
        'citas_hoy': citas_hoy,
        'ultimas_citas': ultimas_citas,
        'medico_usuario': medico_usuario,
        'can_manage_citas': request.user.is_superuser or medico_usuario is not None,
    }
    return render(request, 'core/dashboard.html', context)
