from django import forms
from .models import ModalidadIngreso, ProcesoAdmision, Postulacion, EvaluacionAdmision


class ModalidadIngresoForm(forms.ModelForm):
    class Meta:
        model = ModalidadIngreso
        fields = ['nombre', 'descripcion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProcesoAdmisionForm(forms.ModelForm):
    class Meta:
        model = ProcesoAdmision
        fields = ['nombre', 'year', 'periodo', 'fecha_inicio', 'fecha_fin', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'periodo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class PostulacionForm(forms.ModelForm):
    class Meta:
        model = Postulacion
        fields = ['proceso', 'carrera', 'modalidad', 'estado']
        widgets = {
            'proceso': forms.Select(attrs={'class': 'form-select'}),
            'carrera': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class EvaluacionAdmisionForm(forms.ModelForm):
    class Meta:
        model = EvaluacionAdmision
        fields = ['postulacion', 'nombre', 'fecha', 'puntaje', 'puntaje_maximo', 'observacion']
        widgets = {
            'postulacion': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'puntaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'puntaje_maximo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
