import os
from datetime import date
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misitio.settings')
import django
django.setup()
from clinica_app.models import Medico, BloqueHorario
for m in Medico.objects.all():
    print('---', m, 'activo', m.activo)
    bloques = BloqueHorario.objects.filter(medico=m)
    for b in bloques:
        print('  bloque', b.pk, 'fecha', b.fecha, 'dia', b.dia_semana, 'inicio', b.hora_inicio, 'fin', b.hora_fin)
    fecha = date.today()
    bloquesh = BloqueHorario.bloques_para_medico_fecha(m, fecha)
    print('  aplican hoy:', bloquesh.count())
    for b in bloquesh:
        horas = [t.strftime('%H:%M') for t in b.horas_disponibles()]
        print('    horas', len(horas), horas[:5], '...')
