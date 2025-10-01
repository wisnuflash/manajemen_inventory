from django.db import models


class Category(models.Model):
    """
    Product category model
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'category'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product master data model
    """
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    uom = models.CharField(max_length=20, default='PCS')  # Unit of Measure
    min_stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product'
    
    def __str__(self):
        return f"{self.sku} - {self.name}"


class Supplier(models.Model):
    """
    Supplier model
    """
    name = models.CharField(max_length=150)
    contact = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'supplier'
    
    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    Customer model
    """
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'customer'
    
    def __str__(self):
        return self.name