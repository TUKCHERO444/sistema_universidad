from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def redirect_root(request):
    if request.user.is_authenticated:
        return redirect('cuentas:dashboard')
    return redirect('cuentas:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_root, name='root'),
    path('cuentas/', include('cuentas.urls', namespace='cuentas')),
    path('academico/', include('academico.urls', namespace='academico')),
    path('matriculas/', include('matriculas.urls', namespace='matriculas')),
    path('asistencia/', include('asistencia.urls', namespace='asistencia')),
    path('calificaciones/', include('calificaciones.urls', namespace='calificaciones')),
    path('analitica/', include('analitica.urls', namespace='analitica')),
    path('predicciones/', include('predicciones.urls', namespace='predicciones')),
    path('reportes/', include('reportes.urls', namespace='reportes')),
    path('seguridad/', include('seguridad.urls', namespace='seguridad')),
    path('infraestructura/', include('infraestructura.urls', namespace='infraestructura')),
    path('admision/', include('admision.urls', namespace='admision')),
    path('finanzas/', include('finanzas.urls', namespace='finanzas')),
    path('tramites/', include('tramites.urls', namespace='tramites')),
    path('egresados/', include('egresados.urls', namespace='egresados')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
