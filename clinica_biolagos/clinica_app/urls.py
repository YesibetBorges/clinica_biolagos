from django.urls import path
from . import views

app_name = 'clinica'

urlpatterns = [
    # --- Pacientes ---
    path('pacientes/', views.paciente_lista, name='paciente_lista'),
    path('pacientes/nuevo/', views.paciente_crear, name='paciente_crear'),
    path('pacientes/<int:pk>/', views.paciente_detalle, name='paciente_detalle'),
    path('pacientes/<int:pk>/editar/', views.paciente_editar, name='paciente_editar'),
    path('pacientes/<int:pk>/eliminar/', views.paciente_eliminar, name='paciente_eliminar'),

    # --- Citas ---
    path('solicitar-hora/', views.solicitar_hora, name='solicitar_hora'),
    path('citas/', views.cita_lista, name='cita_lista'),
    path('citas/nueva/', views.cita_crear, name='cita_crear'),
    path('citas/<int:pk>/', views.cita_detalle, name='cita_detalle'),
    path('citas/<int:pk>/editar/', views.cita_editar, name='cita_editar'),
    path('citas/<int:pk>/eliminar/', views.cita_eliminar, name='cita_eliminar'),

    # --- Médicos ---
    path('medicos/', views.medico_lista, name='medico_lista'),
    path('medicos/nuevo/', views.medico_crear, name='medico_crear'),
    path('medicos/<int:pk>/editar/', views.medico_editar, name='medico_editar'),
    path('medicos/<int:pk>/eliminar/', views.medico_eliminar, name='medico_eliminar'),

    # --- Bloques Horarios ---
    path('bloques/', views.bloque_lista, name='bloque_lista'),
    path('bloques/<int:medico_pk>/', views.bloque_lista, name='bloque_lista_medico'),
    path('bloques/<int:pk>/editar/', views.bloque_editar, name='bloque_editar'),
    path('bloques/eliminar/<int:pk>/', views.bloque_eliminar, name='bloque_eliminar'),

    # --- API ---
    path('api/horas-disponibles/', views.horas_disponibles_json, name='horas_disponibles_json'),
]
