from django import forms
from .models import TipoTramite, SolicitudTramite, SeguimientoTramite


class TipoTramiteForm(forms.ModelForm):
    class Meta:
        model = TipoTramite
        fields = ['nombre', 'descripcion', 'costo', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SolicitudTramiteForm(forms.ModelForm):
    class Meta:
        model = SolicitudTramite
        fields = ['estudiante', 'tipo_tramite', 'motivo', 'estado']
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'tipo_tramite': forms.Select(attrs={'class': 'form-select'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class SeguimientoTramiteForm(forms.ModelForm):
    class Meta:
        model = SeguimientoTramite
        fields = ['solicitud', 'estado', 'observacion']
        widgets = {
            'solicitud': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
