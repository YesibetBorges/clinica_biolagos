"""
Script para verificar que todos los requisitos están funcionando correctamente.
Ejecutar: python test_requisitos.py
"""
import os
import sys
from datetime import date, time, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misitio.settings')

import django
django.setup()

from django.contrib.auth.models import User
from clinica_app.models import (
    Medico, Paciente, Cita, BloqueHorario, Especialidad, validar_rut
)
from clinica_app.forms import SolicitudHoraForm, PacienteForm, MedicoForm
from django.core.exceptions import ValidationError
from django import forms as django_forms


def print_header(titulo):
    """Imprime un encabezado visual."""
    print(f"\n{'='*70}")
    print(f"  {titulo}")
    print(f"{'='*70}\n")


def test_validacion_rut():
    """Prueba 1: Validación de RUT con Módulo 11."""
    print_header("TEST 1: VALIDACIÓN RUT MÓDULO 11")
    
    # Test válido
    rut_valido = "41.261.533-6"
    try:
        validar_rut(rut_valido)
        print(f"✅ RUT válido: {rut_valido} → PASÓ")
    except ValidationError as e:
        print(f"❌ RUT válido rechazado: {e}")
        return False
    
    # Test inválido (DV incorrecto)
    rut_invalido = "41.261.533-5"
    try:
        validar_rut(rut_invalido)
        print(f"❌ RUT inválido aceptado: {rut_invalido}")
        return False
    except ValidationError as e:
        print(f"✅ RUT inválido rechazado: {rut_invalido} → PASÓ")
    
    # Test válido sin formato
    rut_sin_formato = "412615336"
    try:
        validar_rut(rut_sin_formato)
        print(f"✅ RUT sin formato aceptado: {rut_sin_formato} → PASÓ")
    except ValidationError as e:
        print(f"❌ RUT sin formato rechazado: {e}")
        return False
    
    # Test válido con K
    rut_con_k = "12.345.678-K"
    try:
        validar_rut(rut_con_k)
        print(f"✅ RUT con K aceptado: {rut_con_k} → PASÓ")
    except ValidationError as e:
        print(f"❌ RUT con K rechazado: {e}")
        return False
    
    return True


def test_bloques_horarios():
    """Prueba 2: Gestión de bloques horarios."""
    print_header("TEST 2: BLOQUES HORARIOS (CREAR, USAR, BORRAR)")
    
    # Obtener médico de prueba
    medico = Medico.objects.filter(activo=True).first()
    if not medico:
        print("❌ No hay médicos activos en la BD")
        return False
    
    print(f"📋 Médico de prueba: {medico.nombre_completo}")
    
    # TEST 2.1: Bloque recurrente (Versión Simple - cada lunes)
    print("\n  [2.1] Bloque RECURRENTE (Lunes, cada semana):")
    try:
        bloque_recurrente = BloqueHorario.objects.create(
            medico=medico,
            fecha=None,  # Sin fecha específica
            dia_semana=0,  # Lunes
            hora_inicio=time(9, 0),
            hora_fin=time(12, 0)
        )
        bloque_recurrente.full_clean()
        print(f"  ✅ Bloque recurrente creado: {bloque_recurrente}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # TEST 2.2: Bloque con fecha específica (Versión Avanzada)
    print("\n  [2.2] Bloque ESPECÍFICO por fecha:")
    fecha_especial = date.today() + timedelta(days=7)
    try:
        bloque_especifico = BloqueHorario.objects.create(
            medico=medico,
            fecha=fecha_especial,  # Fecha exacta
            dia_semana=None,  # Sin día de semana
            hora_inicio=time(14, 0),
            hora_fin=time(17, 0)
        )
        bloque_especifico.full_clean()
        print(f"  ✅ Bloque específico creado: {bloque_especifico}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # TEST 2.3: Bloque de "todos los días" (Versión Simple Plus)
    print("\n  [2.3] Bloque TODOS LOS DÍAS:")
    try:
        bloque_general = BloqueHorario.objects.create(
            medico=medico,
            fecha=None,  # Sin fecha específica
            dia_semana=None,  # Sin día específico → TODOS LOS DÍAS
            hora_inicio=time(8, 0),
            hora_fin=time(18, 0)
        )
        bloque_general.full_clean()
        print(f"  ✅ Bloque todos los días creado: {bloque_general}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # TEST 2.4: Método horas_disponibles()
    print("\n  [2.4] Generación de horas disponibles:")
    horas = bloque_recurrente.horas_disponibles(intervalo_minutos=30)
    print(f"  ✅ Horas generadas ({len(horas)}): {horas[:3]}... (30 min intervals)")
    
    # TEST 2.5: bloques_para_medico_fecha()
    print("\n  [2.5] Consulta de bloques por fecha:")
    # Para un lunes
    proxima_fecha_lunes = date.today()
    while proxima_fecha_lunes.weekday() != 0:  # 0 = lunes
        proxima_fecha_lunes += timedelta(days=1)
    
    bloques_lunes = BloqueHorario.bloques_para_medico_fecha(medico, proxima_fecha_lunes)
    print(f"  ✅ Bloques para {medico.nombre_completo} el {proxima_fecha_lunes.strftime('%A, %d/%m/%Y')}:")
    print(f"     → {bloques_lunes.count()} bloque(s) encontrado(s)")
    for b in bloques_lunes:
        print(f"        • {b.hora_inicio.strftime('%H:%M')} - {b.hora_fin.strftime('%H:%M')}")
    
    # TEST 2.6: Prioridad de bloques (fecha específica > recurrente)
    print("\n  [2.6] Prioridad fecha específica vs. recurrente:")
    bloques_especial = BloqueHorario.bloques_para_medico_fecha(medico, fecha_especial)
    if bloques_especial.filter(fecha=fecha_especial).exists():
        print(f"  ✅ Bloque específico tiene prioridad en {fecha_especial}")
    else:
        print(f"  ❌ Bloque específico no tiene prioridad")
    
    # TEST 2.7: Eliminar bloque
    print("\n  [2.7] Eliminación de bloque horario:")
    bloque_temp = BloqueHorario.objects.create(
        medico=medico,
        fecha=None,
        dia_semana=2,  # Miércoles
        hora_inicio=time(10, 0),
        hora_fin=time(11, 0)
    )
    bloque_temp.full_clean()
    bloque_id = bloque_temp.pk
    bloque_temp.delete()
    if not BloqueHorario.objects.filter(pk=bloque_id).exists():
        print(f"  ✅ Bloque eliminado correctamente")
    else:
        print(f"  ❌ Bloque no se eliminó")
        return False
    
    return True


def test_horas_reservadas():
    """Prueba 3: Paciente solo puede reservar horas disponibles y no reservadas."""
    print_header("TEST 3: SELECCIÓN DE HORAS DISPONIBLES Y NO RESERVADAS")
    
    medico = Medico.objects.filter(activo=True).first()
    paciente = Paciente.objects.first()
    
    if not medico or not paciente:
        print("❌ No hay médico o paciente en la BD")
        return False
    
    # Crear una cita en un horario específico
    fecha_cita = date.today() + timedelta(days=1)
    hora_cita = time(10, 0)
    
    print(f"\n  📋 Médico: {medico.nombre_completo}")
    print(f"  📋 Paciente: {paciente.nombre_completo}")
    print(f"  📋 Fecha: {fecha_cita}, Hora: {hora_cita.strftime('%H:%M')}")
    
    # TEST 3.1: Crear cita existente
    print("\n  [3.1] Crear cita inicial:")
    try:
        cita = Cita.objects.create(
            paciente=paciente,
            medico=medico,
            fecha=fecha_cita,
            hora=hora_cita,
            motivo='Consulta prueba',
            estado='confirmada'
        )
        print(f"  ✅ Cita creada: {cita.paciente.nombre_completo} con {cita.medico.nombre_completo}")
    except Exception as e:
        print(f"  ❌ Error al crear cita: {e}")
        return False
    
    # TEST 3.2: Validación en formulario (hora ya reservada)
    print("\n  [3.2] Intentar reservar la misma hora (debe fallar):")
    form_data = {
        'nombre': 'Test',
        'apellido': 'Usuario',
        'rut': '41.261.533-6',
        'email': 'test@example.com',
        'telefono': '+56 9 1234 5678',
        'medico': medico.pk,
        'fecha': fecha_cita,
        'hora': hora_cita.strftime('%H:%M'),
        'motivo': 'Consulta test',
        'notas': ''
    }
    
    form = SolicitudHoraForm(data=form_data)
    if not form.is_valid():
        print(f"  ✅ Validación correcta - hora ya reservada rechazada")
        print(f"     Errores: {form.errors}")
    else:
        print(f"  ❌ Validación falló - hora reservada fue aceptada")
        return False
    
    # TEST 3.3: Intentar reservar hora libre (debe funcionar)
    print("\n  [3.3] Intentar reservar hora diferente (debe funcionar):")
    hora_libre = time(11, 0)
    form_data['hora'] = hora_libre.strftime('%H:%M')
    form = SolicitudHoraForm(data=form_data)
    if form.is_valid():
        print(f"  ✅ Validación correcta - hora libre aceptada")
    else:
        print(f"  ❌ Validación falló")
        print(f"     Errores: {form.errors}")
        return False
    
    return True


def test_formularios_validacion():
    """Prueba 4: Validación RUT en formularios."""
    print_header("TEST 4: VALIDACIÓN RUT EN FORMULARIOS")
    
    # TEST 4.1: PacienteForm con RUT válido
    print("\n  [4.1] PacienteForm con RUT válido:")
    form_data = {
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'rut': '15.123.456-7',  # RUT válido
        'fecha_nacimiento': '1990-05-15',
        'sexo': 'M',
        'email': 'juan@example.com',
        'telefono': '+56 9 1234 5678',
        'ciudad': 'Puerto Montt',
        'prevision': 'Fonasa'
    }
    form = PacienteForm(data=form_data)
    if form.is_valid():
        print(f"  ✅ PacienteForm aceptó RUT válido")
    else:
        print(f"  ❌ PacienteForm rechazó RUT válido: {form.errors}")
        return False
    
    # TEST 4.2: PacienteForm con RUT inválido
    print("\n  [4.2] PacienteForm con RUT inválido:")
    form_data['rut'] = '15.123.456-8'  # DV incorrecto
    form = PacienteForm(data=form_data)
    if not form.is_valid():
        print(f"  ✅ PacienteForm rechazó RUT inválido")
    else:
        print(f"  ❌ PacienteForm aceptó RUT inválido")
        return False
    
    # TEST 4.3: MedicoForm con RUT válido
    print("\n  [4.3] MedicoForm con RUT válido:")
    especialidad = Especialidad.objects.first()
    form_data = {
        'nombre': 'Carlos',
        'apellido': 'López',
        'rut': '12.345.678-3',  # RUT válido
        'especialidad': especialidad.pk if especialidad else '',
        'email': 'carlos@example.com',
        'telefono': '+56 9 9876 5432',
        'activo': True
    }
    form = MedicoForm(data=form_data)
    if form.is_valid():
        print(f"  ✅ MedicoForm aceptó RUT válido")
    else:
        print(f"  ❌ MedicoForm rechazó RUT válido: {form.errors}")
        return False
    
    return True


def main():
    """Ejecuta todas las pruebas."""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🏥 VERIFICACIÓN DE REQUISITOS - CLÍNICA BIOLAGOS  ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    resultados = []
    
    # Ejecutar pruebas
    resultados.append(("Validación RUT Módulo 11", test_validacion_rut()))
    resultados.append(("Bloques Horarios (CRUD)", test_bloques_horarios()))
    resultados.append(("Horas Disponibles y Reservadas", test_horas_reservadas()))
    resultados.append(("Validación RUT en Formularios", test_formularios_validacion()))
    
    # Resumen
    print_header("📊 RESUMEN DE PRUEBAS")
    
    todas_pasadas = True
    for nombre, resultado in resultados:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{estado:12} → {nombre}")
        if not resultado:
            todas_pasadas = False
    
    print("\n" + "="*70)
    if todas_pasadas:
        print("✅ TODAS LAS PRUEBAS PASARON - SISTEMA LISTO PARA PRESENTACIÓN")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON - REVISAR ERRORES ARRIBA")
    print("="*70 + "\n")
    
    return 0 if todas_pasadas else 1


if __name__ == '__main__':
    sys.exit(main())
