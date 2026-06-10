from django.contrib import admin
from .models import Especialidad, Medico, Paciente, Cita, BloqueHorario


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'rut', 'especialidad', 'email', 'activo']
    list_filter = ['especialidad', 'activo']
    search_fields = ['nombre', 'apellido', 'rut']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'rut', 'telefono', 'prevision', 'fecha_registro']
    list_filter = ['sexo', 'ciudad', 'prevision']
    search_fields = ['nombre', 'apellido', 'rut', 'email']
    readonly_fields = ['fecha_registro']


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'fecha', 'hora', 'estado']
    list_filter = ['estado', 'medico', 'fecha']
    search_fields = ['paciente__nombre', 'paciente__apellido', 'medico__apellido']
    date_hierarchy = 'fecha'


@admin.register(BloqueHorario)
class BloqueHorarioAdmin(admin.ModelAdmin):
    list_display = ['medico', 'get_tipo', 'get_dia_o_fecha', 'hora_inicio', 'hora_fin']
    list_filter = ['medico', 'dia_semana']
    search_fields = ['medico__nombre', 'medico__apellido']

    @admin.display(description='Tipo')
    def get_tipo(self, obj):
        return 'Fecha específica' if obj.fecha else 'Recurrente (día semana)'

    @admin.display(description='Día / Fecha')
    def get_dia_o_fecha(self, obj):
        if obj.fecha:
            return obj.fecha.strftime('%d/%m/%Y')
        return obj.get_dia_semana_display()
