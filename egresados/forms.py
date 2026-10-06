from django import forms
from .models import Egreso, GradoAcademico, Titulacion


class EgresoForm(forms.ModelForm):
    class Meta:
        model = Egreso
        fields = ['estudiante', 'fecha_egreso', 'creditos_aprobados', 'promedio_general', 'observacion']
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'fecha_egreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'creditos_aprobados': forms.NumberInput(attrs={'class': 'form-control'}),
            'promedio_general': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class GradoAcademicoForm(forms.ModelForm):
    class Meta:
        model = GradoAcademico
        fields = ['egreso', 'tipo', 'nombre', 'fecha_otorgamiento', 'numero_registro']
        widgets = {
            'egreso': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_otorgamiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'numero_registro': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TitulacionForm(forms.ModelForm):
    class Meta:
        model = Titulacion
        fields = ['egreso', 'titulo', 'modalidad', 'fecha_sustentacion', 'fecha_otorgamiento', 'numero_registro', 'estado']
        widgets = {
            'egreso': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'modalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_sustentacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_otorgamiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'numero_registro': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
