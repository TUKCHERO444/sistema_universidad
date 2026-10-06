from django import forms
from .models import Aula, Horario, CalendarioAcademico


class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['codigo', 'nombre', 'pabellon', 'piso', 'capacidad', 'tipo', 'estado']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'pabellon': forms.TextInput(attrs={'class': 'form-control'}),
            'piso': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['seccion', 'aula', 'dia_semana', 'hora_inicio', 'hora_fin']
        widgets = {
            'seccion': forms.Select(attrs={'class': 'form-select'}),
            'aula': forms.Select(attrs={'class': 'form-select'}),
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class CalendarioAcademicoForm(forms.ModelForm):
    class Meta:
        model = CalendarioAcademico
        fields = ['periodo', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'periodo': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
