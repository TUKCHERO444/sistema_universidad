# Generated for tramites app

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academico', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoTramite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, unique=True, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('costo', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Costo')),
                ('estado', models.BooleanField(default=True, verbose_name='Estado')),
            ],
            options={
                'verbose_name': 'Tipo de Trámite',
                'verbose_name_plural': 'Tipos de Trámite',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='SolicitudTramite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_solicitud', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Solicitud')),
                ('motivo', models.TextField(blank=True, null=True, verbose_name='Motivo')),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('EN_REVISION', 'En Revisión'), ('APROBADA', 'Aprobada'), ('RECHAZADA', 'Rechazada'), ('CANCELADA', 'Cancelada')], default='PENDIENTE', max_length=15, verbose_name='Estado')),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='solicitudes_tramite', to='academico.estudiante', verbose_name='Estudiante')),
                ('tipo_tramite', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='solicitudes', to='tramites.tipotramite', verbose_name='Tipo de Trámite')),
            ],
            options={
                'verbose_name': 'Solicitud de Trámite',
                'verbose_name_plural': 'Solicitudes de Trámite',
                'ordering': ['-fecha_solicitud'],
            },
        ),
        migrations.CreateModel(
            name='SeguimientoTramite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Seguimiento')),
                ('estado', models.CharField(max_length=50, verbose_name='Estado')),
                ('observacion', models.TextField(blank=True, null=True, verbose_name='Observación')),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seguimientos', to='tramites.solicitudtramite', verbose_name='Solicitud de Trámite')),
            ],
            options={
                'verbose_name': 'Seguimiento de Trámite',
                'verbose_name_plural': 'Seguimientos de Trámite',
                'ordering': ['-fecha'],
            },
        ),
    ]
