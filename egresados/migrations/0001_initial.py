# Generated for egresados app

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academico', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Egreso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_egreso', models.DateField(verbose_name='Fecha de Egreso')),
                ('creditos_aprobados', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Créditos Aprobados')),
                ('promedio_general', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Promedio General')),
                ('observacion', models.TextField(blank=True, null=True, verbose_name='Observación')),
                ('estudiante', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='egreso', to='academico.estudiante', verbose_name='Estudiante')),
            ],
            options={
                'verbose_name': 'Egreso',
                'verbose_name_plural': 'Egresos',
                'ordering': ['-fecha_egreso'],
            },
        ),
        migrations.CreateModel(
            name='GradoAcademico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('BACHILLER', 'Bachiller'), ('MAESTRO', 'Maestro'), ('DOCTOR', 'Doctor')], max_length=10, verbose_name='Tipo de Grado')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre del Grado')),
                ('fecha_otorgamiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Otorgamiento')),
                ('numero_registro', models.CharField(blank=True, max_length=100, null=True, verbose_name='Número de Registro')),
                ('egreso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grados', to='egresados.egreso', verbose_name='Egreso')),
            ],
            options={
                'verbose_name': 'Grado Académico',
                'verbose_name_plural': 'Grados Académicos',
                'ordering': ['-fecha_otorgamiento'],
            },
        ),
        migrations.CreateModel(
            name='Titulacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('modalidad', models.CharField(blank=True, max_length=100, null=True, verbose_name='Modalidad de Titulación')),
                ('fecha_sustentacion', models.DateField(blank=True, null=True, verbose_name='Fecha de Sustentación')),
                ('fecha_otorgamiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Otorgamiento')),
                ('numero_registro', models.CharField(blank=True, max_length=100, null=True, verbose_name='Número de Registro')),
                ('estado', models.CharField(choices=[('EN_PROCESO', 'En Proceso'), ('APROBADO', 'Aprobado'), ('OTORGADO', 'Otorgado')], default='EN_PROCESO', max_length=10, verbose_name='Estado')),
                ('egreso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='titulaciones', to='egresados.egreso', verbose_name='Egreso')),
            ],
            options={
                'verbose_name': 'Titulación',
                'verbose_name_plural': 'Titulaciones',
                'ordering': ['-fecha_sustentacion'],
            },
        ),
    ]
