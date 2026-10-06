from django import forms
from .models import ConceptoPago, CuentaCobrar, Pago, Comprobante


class ConceptoPagoForm(forms.ModelForm):
    class Meta:
        model = ConceptoPago
        fields = ['codigo', 'nombre', 'descripcion', 'estado']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CuentaCobrarForm(forms.ModelForm):
    class Meta:
        model = CuentaCobrar
        fields = ['estudiante', 'periodo', 'concepto', 'monto', 'descuento', 'fecha_emision', 'fecha_vencimiento', 'estado']
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'periodo': forms.Select(attrs={'class': 'form-select'}),
            'concepto': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_emision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['cuenta', 'monto', 'metodo', 'numero_operacion', 'estado']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'metodo': forms.Select(attrs={'class': 'form-select'}),
            'numero_operacion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields = ['pago', 'tipo', 'serie', 'numero']
        widgets = {
            'pago': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
        }
