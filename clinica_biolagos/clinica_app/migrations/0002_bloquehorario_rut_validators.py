"""
Migración 0002:
- Agrega validador validar_rut a los campos rut de Medico y Paciente.
- Crea el modelo BloqueHorario con soporte para bloques recurrentes (dia_semana)
  y bloques por fecha específica (versión avanzada/opcional).
"""
from django.db import migrations, models
import django.db.models.deletion
import clinica_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('clinica_app', '0001_initial'),
    ]

    operations = [
        # --- Validador RUT en Medico ---
        migrations.AlterField(
            model_name='medico',
            name='rut',
            field=models.CharField(
                max_length=12, unique=True,
                validators=[clinica_app.models.validar_rut]
            ),
        ),
        # --- Validador RUT en Paciente ---
        migrations.AlterField(
            model_name='paciente',
            name='rut',
            field=models.CharField(
                max_length=12, unique=True,
                validators=[clinica_app.models.validar_rut]
            ),
        ),
        # --- Nuevo modelo BloqueHorario ---
        migrations.CreateModel(
            name='BloqueHorario',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                # Versión avanzada opcional: fecha específica
                ('fecha', models.DateField(
                    blank=True, null=True,
                    verbose_name='Fecha específica',
                    help_text='Dejar vacío para bloque recurrente semanal.'
                )),
                # Versión simple: día de la semana recurrente
                ('dia_semana', models.IntegerField(
                    blank=True, null=True,
                    verbose_name='Día de la semana',
                    choices=[
                        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
                        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
                    ],
                    help_text='Se usa cuando no se especifica fecha exacta.'
                )),
                ('hora_inicio', models.TimeField(verbose_name='Hora inicio')),
                ('hora_fin', models.TimeField(verbose_name='Hora fin')),
                ('medico', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bloques_horarios',
                    to='clinica_app.medico',
                    verbose_name='Médico'
                )),
            ],
            options={
                'verbose_name': 'Bloque Horario',
                'verbose_name_plural': 'Bloques Horarios',
                'ordering': ['medico', 'dia_semana', 'fecha', 'hora_inicio'],
            },
        ),
    ]
