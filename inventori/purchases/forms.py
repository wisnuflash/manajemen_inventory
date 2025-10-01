from django import forms
from .models import PurchaseOrder, POItem, GoodsReceipt
from master.models import Product, Supplier
from inventory.models import Warehouse


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'supplier', 'warehouse']
        widgets = {
            'po_number': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
        }


class POItemForm(forms.ModelForm):
    product_sku = forms.CharField(max_length=50, label='SKU Produk', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Masukkan SKU produk',
        'id': 'product_sku'
    }))
    
    class Meta:
        model = POItem
        fields = ['qty', 'price']
        widgets = {
            'qty': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values if editing
        if self.instance and self.instance.pk and self.instance.product:
            self.fields['product_sku'].initial = self.instance.product.sku


class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = ['grn_number', 'warehouse', 'purchase_order']
        widgets = {
            'grn_number': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'purchase_order': forms.Select(attrs={'class': 'form-control'}),
        }