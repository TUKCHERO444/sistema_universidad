from .models import RegistroAuditoria

def registrar_auditoria(usuario, modulo, accion, descripcion, request=None):
    ip = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

    return RegistroAuditoria.objects.create(
        usuario=usuario if usuario and getattr(usuario, 'is_authenticated', False) else None,
        modulo=modulo,
        accion=accion,
        descripcion=descripcion,
        ip_address=ip
    )
