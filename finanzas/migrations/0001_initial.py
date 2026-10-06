# Generated for finanzas app

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academico', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConceptoPago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('estado', models.BooleanField(default=True, verbose_name='Estado')),
            ],
            options={
                'verbose_name': 'Concepto de Pago',
                'verbose_name_plural': 'Conceptos de Pago',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='CuentaCobrar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monto')),
                ('descuento', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Descuento')),
                ('fecha_emision', models.DateField(verbose_name='Fecha de Emisión')),
                ('fecha_vencimiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('PARCIAL', 'Parcial'), ('PAGADO', 'Pagado'), ('ANULADO', 'Anulado')], default='PENDIENTE', max_length=10, verbose_name='Estado')),
                ('concepto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cuentas', to='finanzas.conceptopago', verbose_name='Concepto de Pago')),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cuentas_cobrar', to='academico.estudiante', verbose_name='Estudiante')),
                ('periodo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cuentas_cobrar', to='academico.periodo', verbose_name='Periodo Académico')),
            ],
            options={
                'verbose_name': 'Cuenta por Cobrar',
                'verbose_name_plural': 'Cuentas por Cobrar',
                'ordering': ['-fecha_emision'],
            },
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monto')),
                ('fecha_pago', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Pago')),
                ('metodo', models.CharField(choices=[('EFECTIVO', 'Efectivo'), ('TARJETA', 'Tarjeta'), ('TRANSFERENCIA', 'Transferencia'), ('BANCO', 'Banco'), ('OTRO', 'Otro')], max_length=15, verbose_name='Método de Pago')),
                ('numero_operacion', models.CharField(blank=True, max_length=100, null=True, verbose_name='Número de Operación')),
                ('estado', models.CharField(choices=[('REGISTRADO', 'Registrado'), ('ANULADO', 'Anulado')], default='REGISTRADO', max_length=10, verbose_name='Estado')),
                ('cuenta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='finanzas.cuentacobrar', verbose_name='Cuenta por Cobrar')),
            ],
            options={
                'verbose_name': 'Pago',
                'verbose_name_plural': 'Pagos',
                'ordering': ['-fecha_pago'],
            },
        ),
        migrations.CreateModel(
            name='Comprobante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('BOLETA', 'Boleta'), ('FACTURA', 'Factura'), ('RECIBO', 'Recibo')], max_length=10, verbose_name='Tipo de Comprobante')),
                ('serie', models.CharField(blank=True, max_length=10, null=True, verbose_name='Serie')),
                ('numero', models.CharField(blank=True, max_length=20, null=True, verbose_name='Número')),
                ('fecha_emision', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Emisión')),
                ('pago', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='comprobante', to='finanzas.pago', verbose_name='Pago')),
            ],
            options={
                'verbose_name': 'Comprobante',
                'verbose_name_plural': 'Comprobantes',
                'ordering': ['-fecha_emision'],
            },
        ),
    ]
