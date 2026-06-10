from .access import is_medico_user, is_paciente_user


def user_role_flags(request):
    return {
        'is_medico_user': is_medico_user(request.user),
        'is_paciente_user': is_paciente_user(request.user),
    }
