from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin

def role_required(roles_permitidos):
    """
    Decorador para restringir acceso a vistas basadas en funciones.
    roles_permitidos puede ser una lista de roles o un string único.
    """
    if isinstance(roles_permitidos, str):
        roles_permitidos = [roles_permitidos]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('cuentas:login')
            
            # Superusuario siempre tiene acceso total
            if request.user.is_superuser or request.user.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'No tienes permisos suficientes para acceder a este recurso.')
            raise PermissionDenied("Acceso restringido por rol institucional.")
        return _wrapped_view
    return decorator

class RoleRequiredMixin(AccessMixin):
    """Mixin para vistas basadas en clases."""
    roles_permitidos = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser or request.user.rol in self.roles_permitidos:
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, 'No tienes permisos suficientes para acceder a este recurso.')
        raise PermissionDenied("Acceso restringido por rol institucional.")
