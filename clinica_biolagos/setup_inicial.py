"""
Configuracion inicial para Clinica BioLagos.

Ejecutar despues de aplicar migraciones:
    python setup_inicial.py
"""
import os
from datetime import date, time

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misitio.settings')
django.setup()

from django.contrib.auth.models import User
from clinica_app.models import BloqueHorario, Cita, Especialidad, Medico, Paciente


def crear_usuarios():
    admin, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@clinicabiolagos.cl',
            'is_staff': True,
            'is_superuser': True,
        },
    )
    admin.email = 'admin@clinicabiolagos.cl'
    admin.is_staff = True
    admin.is_superuser = True
    admin.set_password('admin123')
    admin.save()

    yesi, _ = User.objects.get_or_create(username='yesi')
    yesi.email = 'yesi@prueba.cl'
    yesi.first_name = 'Yesi'
    yesi.last_name = 'Borges'
    yesi.is_staff = False
    yesi.is_superuser = False
    yesi.set_password('Yesi1234')
    yesi.save()

    carlos, _ = User.objects.get_or_create(username='carlos')
    carlos.email = 'cmunoz@clinicabiolagos.cl'
    carlos.first_name = 'Carlos'
    carlos.last_name = 'Munoz'
    carlos.is_staff = False
    carlos.is_superuser = False
    carlos.set_password('Carlos1234')
    carlos.save()

    print("Usuarios creados/actualizados: admin, yesi, carlos")
    return admin


def crear_especialidades():
    nombres = [
        'Medicina General',
        'Cardiologia',
        'Neurologia',
        'Pediatria',
        'Traumatologia',
        'Ginecologia',
        'Dermatologia',
        'Medicina Interna',
    ]
    for nombre in nombres:
        Especialidad.objects.update_or_create(nombre=nombre, defaults={'descripcion': ''})
    print(f"{len(nombres)} especialidades listas.")


def crear_medicos():
    medicos_data = [
        ('Maria', 'Gonzalez', '12.111.222-3', 'Cardiologia', 'mgonzalez@clinicabiolagos.cl', '+56 9 1111 2222'),
        ('Carlos', 'Munoz', '13.222.333-4', 'Neurologia', 'cmunoz@clinicabiolagos.cl', '+56 9 2222 3333'),
        ('Ana', 'Ramirez', '14.333.444-5', 'Pediatria', 'aramirez@clinicabiolagos.cl', '+56 9 3333 4444'),
        ('Jorge', 'Vega', '15.444.555-6', 'Traumatologia', 'jvega@clinicabiolagos.cl', '+56 9 4444 5555'),
        ('Sofia', 'Torres', '16.555.666-7', 'Medicina General', 'storres@clinicabiolagos.cl', '+56 9 5555 6666'),
    ]
    for nombre, apellido, rut, esp, email, tel in medicos_data:
        especialidad = Especialidad.objects.filter(nombre=esp).first()
        Medico.objects.update_or_create(
            rut=rut,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'especialidad': especialidad,
                'email': email,
                'telefono': tel,
                'activo': True,
            },
        )
    print(f"{len(medicos_data)} medicos listos.")


def crear_pacientes(admin):
    pacientes_data = [
        ('Luis', 'Perez', '8.111.222-3', date(1985, 3, 15), 'M', 'lperez@gmail.com', '+56 9 6666 7777', 'Fonasa'),
        ('Carmen', 'Lopez', '9.222.333-4', date(1990, 7, 22), 'F', 'clopez@gmail.com', '+56 9 7777 8888', 'Banmedica'),
        ('Pedro', 'Soto', '10.333.444-5', date(1978, 11, 8), 'M', 'psoto@gmail.com', '+56 9 8888 9999', 'Fonasa'),
        ('Valentina', 'Diaz', '11.444.555-6', date(2001, 4, 30), 'F', 'vdiaz@gmail.com', '+56 9 9999 0000', 'Colmena'),
        ('Roberto', 'Flores', '12.555.666-7', date(1965, 9, 12), 'M', 'rflores@gmail.com', '+56 9 1234 5678', 'Fonasa'),
        ('Yesi', 'Borges', '10634444-4', date(1995, 5, 10), 'F', 'yesi@prueba.cl', '+56 9 5555 4444', 'Fonasa'),
    ]
    for nombre, apellido, rut, fnac, sexo, email, tel, prevision in pacientes_data:
        Paciente.objects.update_or_create(
            rut=rut,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'fecha_nacimiento': fnac,
                'sexo': sexo,
                'email': email,
                'telefono': tel,
                'ciudad': 'Puerto Montt',
                'prevision': prevision,
                'creado_por': admin,
            },
        )
    print(f"{len(pacientes_data)} pacientes listos.")


def crear_bloques(admin):
    carlos = Medico.objects.filter(rut='13.222.333-4').first()
    if carlos:
        BloqueHorario.objects.update_or_create(
            medico=carlos,
            fecha=None,
            dia_semana=None,
            defaults={'hora_inicio': time(9, 0), 'hora_fin': time(17, 0)}
        )
    maria = Medico.objects.filter(rut='12.111.222-3').first()
    if maria:
        BloqueHorario.objects.update_or_create(
            medico=maria,
            fecha=None,
            dia_semana=0,
            defaults={'hora_inicio': time(9, 0), 'hora_fin': time(15, 0)}
        )
    print('Bloques de ejemplo creados para Carlos y María.')


def crear_citas(admin):
    if Cita.objects.count() > 0:
        print("Ya existen citas, se omite la creacion.")
        return

    citas_data = [
        ('8.111.222-3', '12.111.222-3', date(2026, 5, 20), time(9, 0), 'Control cardiovascular anual', 'confirmada'),
        ('12.555.666-7', '13.222.333-4', date(2026, 5, 21), time(10, 30), 'Cefalea cronica', 'pendiente'),
        ('9.222.333-4', '14.333.444-5', date(2026, 5, 22), time(11, 0), 'Control pediatrico familiar', 'confirmada'),
        ('11.444.555-6', '15.444.555-6', date(2026, 5, 23), time(14, 0), 'Dolor lumbar', 'pendiente'),
        ('10.333.444-5', '16.555.666-7', date(2026, 5, 24), time(15, 30), 'Chequeo medico general', 'completada'),
    ]
    for paciente_rut, medico_rut, fecha, hora, motivo, estado in citas_data:
        paciente = Paciente.objects.get(rut=paciente_rut)
        medico = Medico.objects.get(rut=medico_rut)
        Cita.objects.create(
            paciente=paciente,
            medico=medico,
            fecha=fecha,
            hora=hora,
            motivo=motivo,
            estado=estado,
            creado_por=admin,
        )
    print(f"{len(citas_data)} citas listas.")


if __name__ == '__main__':
    print("\nConfigurando Clinica BioLagos...\n")
    admin = crear_usuarios()
    crear_especialidades()
    crear_medicos()
    crear_pacientes(admin)
    crear_bloques(admin)
    crear_citas(admin)
    print("\nConfiguracion inicial completada.")
    print("Admin:   admin / admin123")
    print("Paciente yesi / Yesi1234")
    print("Doctor:  carlos / Carlos1234")
    print("Ejecuta: python manage.py runserver")
    print("Abre:    http://127.0.0.1:8000/\n")
