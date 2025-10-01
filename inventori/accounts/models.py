from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('warehouse', 'Warehouse'),
        ('cashier', 'Cashier'),
        ('analyst', 'Analyst'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Fix the conflicts with Django's built-in User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"