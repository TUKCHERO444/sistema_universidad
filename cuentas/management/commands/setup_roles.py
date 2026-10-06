from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from cuentas.models import Usuario

class Command(BaseCommand):
    help = 'Inicializa los grupos de roles institucionales y usuarios de demostración'

    def handle(self, *args, **options):
        self.stdout.write("Configurando grupos y permisos...")

        # 1. Crear Grupos
        grupo_admin, _ = Group.objects.get_or_create(name='ADMINISTRADORES')
        grupo_docente, _ = Group.objects.get_or_create(name='DOCENTES')
        grupo_estudiante, _ = Group.objects.get_or_create(name='ESTUDIANTES')

        # Asignar permisos estándar a los grupos
        for perm in Permission.objects.all():
            grupo_admin.permissions.add(perm)

        # 2. Crear Superusuario / Admin
        admin_user, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Administrador',
                'last_name': 'General',
                'email': 'admin@universidad.edu.pe',
                'dni': '10000001',
                'rol': Usuario.Rol.ADMIN,
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin123')
        admin_user.groups.add(grupo_admin)
        admin_user.save()

        self.stdout.write(self.style.SUCCESS("Roles y usuario admin (admin / admin123) configurados exitosamente."))
