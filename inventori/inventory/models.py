from django.db import models
from master.models import Product


class Warehouse(models.Model):
    """
    Warehouse model
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warehouse'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Stock(models.Model):
    """
    Stock model (quantity per product per warehouse)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'stock'
        unique_together = ('product', 'warehouse')
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.qty}"


class StockMove(models.Model):
    """
    Stock movement model (audit trail for all stock movements)
    """
    REF_TYPE_CHOICES = [
        ('SALE', 'Sale'),
        ('GRN', 'Goods Receipt'),
        ('ADJUST', 'Adjustment'),
        ('TRANSFER', 'Transfer'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    ref_type = models.CharField(max_length=20, choices=REF_TYPE_CHOICES)
    ref_id = models.BigIntegerField(null=True, blank=True)  # ID of the reference (e.g., Sale ID, GRN ID)
    qty_in = models.IntegerField(default=0)
    qty_out = models.IntegerField(default=0)
    note = models.CharField(max_length=255, blank=True)
    moved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_move'
        indexes = [
            models.Index(fields=['ref_type', 'ref_id'], name='idx_sm_ref'),
            models.Index(fields=['product', 'moved_at'], name='idx_sm_product_date'),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.ref_type} - {self.moved_at}"


class ReorderPolicy(models.Model):
    """
    Reorder policy model (ROP, safety stock, reorder quantity)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    avg_daily_demand = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lead_time_days = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_level = models.DecimalField(max_digits=5, decimal_places=2, default=95.00)  # e.g., 95%
    demand_std = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # standard deviation of demand
    rop = models.IntegerField(default=0)  # Reorder Point
    safety_stock = models.IntegerField(default=0)
    reorder_qty = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'reorder_policy'
        unique_together = ('product', 'warehouse')
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name} - ROP: {self.rop}"