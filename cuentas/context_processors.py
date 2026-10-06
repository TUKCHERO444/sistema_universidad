from academico.models import Periodo

def usuario_contexto(request):
    """Procesador de contexto para inyectar variables globales en las plantillas."""
    periodo_actual = None
    if request.user.is_authenticated:
        try:
            periodo_actual = Periodo.objects.filter(activo=True).order_by('-fecha_inicio').first()
        except Exception:
            periodo_actual = None

    return {
        'ROL_ACTUAL': getattr(request.user, 'rol', None) if request.user.is_authenticated else None,
        'PERIODO_ACTUAL': periodo_actual,
        'ES_ADMIN': request.user.is_authenticated and (request.user.rol == 'ADMIN' or request.user.is_superuser),
        'ES_DOCENTE': request.user.is_authenticated and request.user.rol == 'DOCENTE',
        'ES_ESTUDIANTE': request.user.is_authenticated and request.user.rol == 'ESTUDIANTE',
    }
