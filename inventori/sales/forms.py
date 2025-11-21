from django import forms
from .models import Sale, SaleItem
from master.models import Product, Customer
from inventory.models import Warehouse


class POSForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
        }


class SaleItemForm(forms.ModelForm):
    product_sku = forms.CharField(max_length=50, label='Kode Barang', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Scan atau ketik Kode Barang / Nama',
        'id': 'product_sku'
    }))
    
    class Meta:
        model = SaleItem
        fields = ['qty', 'price']
        widgets = {
            'qty': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'readonly': 'readonly'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values if editing
        if self.instance and self.instance.pk and self.instance.product:
            self.fields['product_sku'].initial = self.instance.product.sku