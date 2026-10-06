from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, RegistroAuditoria

@admin.register(Usuario)
class UsuarioCustomAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'dni', 'rol', 'is_active', 'is_staff')
    list_filter = ('rol', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'dni', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Institucional', {'fields': ('rol', 'dni', 'telefono', 'avatar', 'intentos_fallidos', 'bloqueado_hasta')}),
    )

@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'usuario', 'modulo', 'accion', 'descripcion', 'ip_address')
    list_filter = ('modulo', 'accion', 'fecha_hora')
    search_fields = ('usuario__username', 'descripcion', 'ip_address')
    readonly_fields = ('usuario', 'modulo', 'accion', 'descripcion', 'ip_address', 'fecha_hora')
