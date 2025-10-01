from django import forms
from .models import Warehouse, Stock, StockMove, ReorderPolicy
from master.models import Product


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['code', 'name', 'address']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['product', 'warehouse', 'qty']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'qty': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class StockMoveForm(forms.ModelForm):
    class Meta:
        model = StockMove
        fields = ['product', 'warehouse', 'ref_type', 'ref_id', 'qty_in', 'qty_out', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'ref_type': forms.Select(attrs={'class': 'form-control'}),
            'ref_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'qty_in': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'qty_out': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ReorderPolicyForm(forms.ModelForm):
    class Meta:
        model = ReorderPolicy
        fields = ['product', 'warehouse', 'avg_daily_demand', 'lead_time_days', 'service_level', 'demand_std', 'rop', 'safety_stock', 'reorder_qty']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'avg_daily_demand': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'lead_time_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'service_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'demand_std': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rop': forms.NumberInput(attrs={'class': 'form-control'}),
            'safety_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'reorder_qty': forms.NumberInput(attrs={'class': 'form-control'}),
        }