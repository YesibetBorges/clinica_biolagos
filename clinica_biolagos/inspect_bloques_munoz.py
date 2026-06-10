import os
from datetime import date
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misitio.settings')
import django
django.setup()
from clinica_app.models import Medico, BloqueHorario
m = Medico.objects.filter(apellido__icontains='Munoz').first()
print('Medico:', m, 'activo', getattr(m, 'activo', None))
if m:
    bloques = BloqueHorario.objects.filter(medico=m)
    print('Bloques totales:', bloques.count())
    for b in bloques:
        print(' -', b.pk, 'fecha', b.fecha, 'dia', b.dia_semana, 'inicio', b.hora_inicio, 'fin', b.hora_fin)
    fecha = date.today()
    print('Hoy', fecha, 'weekday', fecha.weekday())
    bloquesh = BloqueHorario.bloques_para_medico_fecha(m, fecha)
    print('Bloques aplican hoy:', bloquesh.count())
    for b in bloquesh:
        print('  *', b.pk, b)
    if bloquesh.exists():
        for b in bloquesh:
            horas = [t.strftime('%H:%M') for t in b.horas_disponibles()]
            print('  horas:', horas[:10], '... total', len(horas))
