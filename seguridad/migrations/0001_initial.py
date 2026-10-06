# Generated for seguridad app

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Permiso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=100, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('descripcion', models.CharField(blank=True, max_length=250, null=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name': 'Permiso',
                'verbose_name_plural': 'Permisos',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True, verbose_name='Nombre')),
                ('descripcion', models.CharField(blank=True, max_length=250, null=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name': 'Rol',
                'verbose_name_plural': 'Roles',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='RolPermiso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permiso', models.ForeignKey(on_delete=models.CASCADE, related_name='roles', to='seguridad.permiso', verbose_name='Permiso')),
                ('rol', models.ForeignKey(on_delete=models.CASCADE, related_name='permisos', to='seguridad.rol', verbose_name='Rol')),
            ],
            options={
                'verbose_name': 'Rol-Permiso',
                'verbose_name_plural': 'Roles-Permisos',
                'unique_together': {('rol', 'permiso')},
            },
        ),
    ]
