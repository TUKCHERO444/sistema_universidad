# Generated for admision app

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academico', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModalidadIngreso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('estado', models.BooleanField(default=True, verbose_name='Estado')),
            ],
            options={
                'verbose_name': 'Modalidad de Ingreso',
                'verbose_name_plural': 'Modalidades de Ingreso',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='ProcesoAdmision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, verbose_name='Nombre del Proceso')),
                ('year', models.PositiveSmallIntegerField(verbose_name='Año')),
                ('periodo', models.CharField(blank=True, max_length=30, null=True, verbose_name='Periodo')),
                ('fecha_inicio', models.DateField(verbose_name='Fecha de Inicio')),
                ('fecha_fin', models.DateField(verbose_name='Fecha de Fin')),
                ('estado', models.CharField(choices=[('PLANIFICADO', 'Planificado'), ('ABIERTO', 'Abierto'), ('CERRADO', 'Cerrado')], default='PLANIFICADO', max_length=15, verbose_name='Estado')),
            ],
            options={
                'verbose_name': 'Proceso de Admisión',
                'verbose_name_plural': 'Procesos de Admisión',
                'ordering': ['-year', '-fecha_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Postulacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_postulacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Postulación')),
                ('estado', models.CharField(choices=[('REGISTRADA', 'Registrada'), ('EN_EVALUACION', 'En Evaluación'), ('ADMITIDA', 'Admitida'), ('NO_ADMITIDA', 'No Admitida'), ('ANULADA', 'Anulada')], default='REGISTRADA', max_length=15, verbose_name='Estado')),
                ('carrera', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='postulaciones', to='academico.carrera', verbose_name='Carrera')),
                ('modalidad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='postulaciones', to='admision.modalidadingreso', verbose_name='Modalidad de Ingreso')),
                ('proceso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postulaciones', to='admision.procesoadmision', verbose_name='Proceso de Admisión')),
            ],
            options={
                'verbose_name': 'Postulación',
                'verbose_name_plural': 'Postulaciones',
                'ordering': ['-fecha_postulacion'],
            },
        ),
        migrations.CreateModel(
            name='EvaluacionAdmision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre de la Evaluación')),
                ('fecha', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Evaluación')),
                ('puntaje', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Puntaje Obtenido')),
                ('puntaje_maximo', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Puntaje Máximo')),
                ('observacion', models.CharField(blank=True, max_length=250, null=True, verbose_name='Observación')),
                ('postulacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluaciones', to='admision.postulacion', verbose_name='Postulación')),
            ],
            options={
                'verbose_name': 'Evaluación de Admisión',
                'verbose_name_plural': 'Evaluaciones de Admisión',
                'ordering': ['fecha'],
            },
        ),
        migrations.CreateModel(
            name='ResultadoAdmision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntaje_final', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Puntaje Final')),
                ('resultado', models.CharField(choices=[('ADMITIDO', 'Admitido'), ('NO_ADMITIDO', 'No Admitido')], max_length=15, verbose_name='Resultado')),
                ('fecha_resultado', models.DateTimeField(auto_now_add=True, verbose_name='Fecha del Resultado')),
                ('postulacion', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resultado', to='admision.postulacion', verbose_name='Postulación')),
            ],
            options={
                'verbose_name': 'Resultado de Admisión',
                'verbose_name_plural': 'Resultados de Admisión',
                'ordering': ['-fecha_resultado'],
            },
        ),
    ]
