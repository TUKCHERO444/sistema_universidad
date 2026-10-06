# Generated for infraestructura app

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academico', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nombre')),
                ('pabellon', models.CharField(blank=True, max_length=100, null=True, verbose_name='Pabellón')),
                ('piso', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Piso')),
                ('capacidad', models.PositiveSmallIntegerField(verbose_name='Capacidad')),
                ('tipo', models.CharField(choices=[('AULA', 'Aula'), ('LABORATORIO', 'Laboratorio'), ('TALLER', 'Taller'), ('AUDITORIO', 'Auditorio')], default='AULA', max_length=15, verbose_name='Tipo')),
                ('estado', models.BooleanField(default=True, verbose_name='Estado')),
            ],
            options={
                'verbose_name': 'Aula',
                'verbose_name_plural': 'Aulas',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='CalendarioAcademico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, verbose_name='Nombre del Evento')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('fecha_inicio', models.DateTimeField(verbose_name='Fecha de Inicio')),
                ('fecha_fin', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Fin')),
            ],
            options={
                'verbose_name': 'Evento de Calendario',
                'verbose_name_plural': 'Eventos de Calendario',
                'ordering': ['fecha_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.CharField(choices=[('LUNES', 'Lunes'), ('MARTES', 'Martes'), ('MIERCOLES', 'Miércoles'), ('JUEVES', 'Jueves'), ('VIERNES', 'Viernes'), ('SABADO', 'Sábado'), ('DOMINGO', 'Domingo')], max_length=10, verbose_name='Día de la Semana')),
                ('hora_inicio', models.TimeField(verbose_name='Hora de Inicio')),
                ('hora_fin', models.TimeField(verbose_name='Hora de Fin')),
                ('aula', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='horarios', to='infraestructura.aula', verbose_name='Aula')),
                ('seccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios', to='academico.seccion', verbose_name='Sección')),
            ],
            options={
                'verbose_name': 'Horario',
                'verbose_name_plural': 'Horarios',
                'ordering': ['dia_semana', 'hora_inicio'],
            },
        ),
        migrations.AddField(
            model_name='calendarioacademico',
            name='periodo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventos', to='academico.periodo', verbose_name='Periodo Académico'),
        ),
    ]
