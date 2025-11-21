from django.db import models
from django.contrib.auth import get_user_model
from master.models import Product, Customer
from inventory.models import Warehouse

User = get_user_model()

class Sale(models.Model):
    """
    Sale header model (POS transaction)
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=40, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    sold_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sale'
        indexes = [
            models.Index(fields=['sold_at', 'status']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.status}"


class SaleItem(models.Model):
    """
    Sale item detail model
    """
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'sale_item'
        indexes = [
            models.Index(fields=['sale_id', 'product_id']),
        ]
    
    def __str__(self):
        return f"{self.sale.invoice_number} - {self.product.name}"
    
    def get_total(self):
        return self.qty * self.price