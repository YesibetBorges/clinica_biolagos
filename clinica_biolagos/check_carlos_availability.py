import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misitio.settings')
django.setup()

from clinica_app.models import Medico, BloqueHorario, Cita

from clinica_app.forms import SolicitudHoraForm

c = Medico.objects.filter(nombre__iexact='Carlos', apellido__iexact='Munoz').first()
print('Carlos', c)
if c:
    fecha = date(2026, 6, 11)
    bloques = BloqueHorario.bloques_para_medico_fecha(c, fecha)
    print('Bloques aplican:', bloques.count())
    for b in bloques:
        horas = [t.strftime('%H:%M') for t in b.horas_disponibles()]
        print('  bloque', b, b.hora_inicio, b.hora_fin, horas, '... total', len(horas))
    ocupadas = list(Cita.objects.filter(medico=c, fecha=fecha).exclude(estado='cancelada').values_list('hora', flat=True))
    print('Ocupadas', [h.strftime('%H:%M') for h in ocupadas])
    horas = sorted({f'{h.hour:02d}:{h.minute:02d}' for b in bloques for h in b.horas_disponibles() if h not in ocupadas})
    print('Disponibles', horas)

    user = type('U', (), {'username':'yesi', 'is_authenticated':True})()
    data = {
        'nombre': 'Yesi',
        'apellido': 'Borges',
        'rut': '10634444-4',
        'email': 'yesi@prueba.cl',
        'telefono': '+56 9 5555 4444',
        'medico': str(c.pk),
        'fecha': '2026-06-11',
        'hora': '21:00',
        'motivo': 'Consulta'
    }
    form = SolicitudHoraForm(data, user=user)
    print('Form bound:', form.is_bound)
    print('Hora choices count:', len(form.fields['hora'].choices))
    print('Hora choices:', form.fields['hora'].choices)
    print('Hora valid 21:00?:', form.fields['hora'].valid_value('21:00'))
    print('Form valid:', form.is_valid())
    print('Errors:', form.errors.as_json())
