from django.db import models
from master.models import Product, Supplier
from inventory.models import Warehouse


class PurchaseOrder(models.Model):
    """
    Purchase Order model
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    po_number = models.CharField(max_length=40, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    ordered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'purchase_order'
    
    def __str__(self):
        return f"{self.po_number} - {self.status}"


class POItem(models.Model):
    """
    Purchase Order Item model
    """
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'po_item'
    
    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.product.name}"
    
    def get_total(self):
        return self.qty * self.price


class GoodsReceipt(models.Model):
    """
    Goods Receipt Note model
    """
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, null=True, blank=True)
    grn_number = models.CharField(max_length=40, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'goods_receipt'
    
    def __str__(self):
        return f"{self.grn_number} - {self.received_at}"