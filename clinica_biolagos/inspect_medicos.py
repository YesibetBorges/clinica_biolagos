import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misitio.settings')
import django
django.setup()
from clinica_app.models import Medico
for m in Medico.objects.all():
    print(m.pk, m.nombre, m.apellido, m.email, m.activo)
