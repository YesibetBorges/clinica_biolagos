from django.db.models import Q

from .models import BloqueHorario, Cita, Medico, Paciente


def get_user_medico(user):
    if not user.is_authenticated:
        return None
    email = (user.email or '').strip()
    if not email:
        return None
    return Medico.objects.filter(email__iexact=email).first()


def get_user_paciente(user):
    if not user.is_authenticated:
        return None
    email = (user.email or '').strip()
    if not email:
        return None
    return Paciente.objects.filter(email__iexact=email).first()


def is_medico_user(user):
    return get_user_medico(user) is not None


def is_paciente_user(user):
    return get_user_paciente(user) is not None


def paciente_queryset_for_user(user):
    qs = Paciente.objects.all()
    if user.is_superuser:
        return qs

    medico = get_user_medico(user)
    paciente = get_user_paciente(user)
    filters = Q(creado_por=user)

    if medico:
        filters |= Q(citas__medico=medico)
    if paciente:
        filters |= Q(pk=paciente.pk)

    return qs.filter(filters).distinct()


def cita_queryset_for_user(user):
    qs = Cita.objects.select_related('paciente', 'medico')
    if user.is_superuser:
        return qs

    medico = get_user_medico(user)
    paciente = get_user_paciente(user)
    filters = Q()
    has_role_scope = False

    if medico:
        filters |= Q(medico=medico)
        has_role_scope = True
    if paciente:
        filters |= Q(paciente=paciente)
        has_role_scope = True
    if not has_role_scope:
        filters = Q(creado_por=user)

    return qs.filter(filters).distinct()


def can_access_paciente(user, paciente):
    return paciente_queryset_for_user(user).filter(pk=paciente.pk).exists()


def bloque_queryset_for_user(user):
    qs = BloqueHorario.objects.select_related('medico')
    if user.is_superuser:
        return qs

    medico = get_user_medico(user)
    if medico:
        return qs.filter(medico=medico)
    return qs.none()


def can_access_bloque(user, bloque):
    return bloque_queryset_for_user(user).filter(pk=bloque.pk).exists()


def can_access_cita(user, cita):
    return cita_queryset_for_user(user).filter(pk=cita.pk).exists()
