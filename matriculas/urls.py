from django.urls import path
from . import views

app_name = 'matriculas'

urlpatterns = [
    path('', views.matricula_list_view, name='matricula_list'),
    path('nueva/', views.matricula_create_view, name='matricula_create'),
    path('<int:pk>/', views.matricula_detail_view, name='matricula_detail'),
    path('<int:pk>/anular/', views.matricula_anular_view, name='matricula_anular'),
    path('mis-matriculas/', views.mis_matriculas_view, name='mis_matriculas'),
]
