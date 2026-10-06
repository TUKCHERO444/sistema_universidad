from django import forms
from .models import Carrera, Curso, Periodo, Docente, Estudiante, Seccion, Facultad, PlanEstudio, PlanCurso


class FacultadForm(forms.ModelForm):
    class Meta:
        model = Facultad
        fields = ['codigo', 'nombre', 'estado']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ['codigo', 'nombre', 'descripcion', 'facultad', 'duracion_ciclos', 'grado_academico', 'titulo_profesional', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'facultad': forms.Select(attrs={'class': 'form-select'}),
            'duracion_ciclos': forms.NumberInput(attrs={'class': 'form-control'}),
            'grado_academico': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo_profesional': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PlanEstudioForm(forms.ModelForm):
    class Meta:
        model = PlanEstudio
        fields = ['carrera', 'codigo', 'nombre', 'year_inicio', 'total_creditos', 'estado']
        widgets = {
            'carrera': forms.Select(attrs={'class': 'form-select'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'year_inicio': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_creditos': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class PlanCursoForm(forms.ModelForm):
    class Meta:
        model = PlanCurso
        fields = ['plan', 'curso', 'ciclo', 'creditos', 'tipo']
        widgets = {
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'ciclo': forms.NumberInput(attrs={'class': 'form-control'}),
            'creditos': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['codigo', 'nombre', 'carrera', 'ciclo', 'creditos', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'carrera': forms.Select(attrs={'class': 'form-select'}),
            'ciclo': forms.NumberInput(attrs={'class': 'form-control'}),
            'creditos': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['codigo', 'nombre', 'fecha_inicio', 'fecha_fin', 'matricula_inicio', 'matricula_fin', 'estado', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'matricula_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'matricula_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = ['codigo', 'dni', 'nombres', 'apellidos', 'correo', 'telefono', 'especialidad', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['codigo', 'dni', 'nombres', 'apellidos', 'correo', 'telefono', 'fecha_nacimiento', 'carrera', 'estado']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'carrera': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['curso', 'periodo', 'docente', 'codigo_seccion', 'capacidad_maxima', 'fecha_corte_predictivo', 'activo']
        widgets = {
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'periodo': forms.Select(attrs={'class': 'form-select'}),
            'docente': forms.Select(attrs={'class': 'form-select'}),
            'codigo_seccion': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_corte_predictivo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
