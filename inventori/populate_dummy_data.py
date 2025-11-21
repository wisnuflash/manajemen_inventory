#!/usr/bin/env python
"""
Script to populate the database with dummy data
"""

import os
import sys
import django
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random

# Setup Django environment
sys.path.append('/Users/wisnuflash/development/adron/manajemen_inventory/inventori')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventori.settings')
django.setup()

from master.models import Category, Product, Customer
from inventory.models import Warehouse, Stock, ReorderPolicy
from sales.models import Sale, SaleItem
from purchases.models import PurchaseOrder, POItem, GoodsReceipt
from mining.models import AssociationRule

User = get_user_model()

def create_users():
    print('Creating users...')
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'role': 'admin',
            'is_staff': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
    # Create manager user
    manager_user, created = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@example.com',
            'role': 'manager'
        }
    )
    if created:
        manager_user.set_password('manager123')
        manager_user.save()
    
    # Create cashier user
    cashier_user, created = User.objects.get_or_create(
        username='cashier',
        defaults={
            'email': 'cashier@example.com',
            'role': 'cashier'
        }
    )
    if created:
        cashier_user.set_password('cashier123')
        cashier_user.save()
    
    # Create warehouse user
    warehouse_user, created = User.objects.get_or_create(
        username='warehouse',
        defaults={
            'email': 'warehouse@example.com',
            'role': 'warehouse'
        }
    )
    if created:
        warehouse_user.set_password('warehouse123')
        warehouse_user.save()
    
    # Create analyst user
    analyst_user, created = User.objects.get_or_create(
        username='analyst',
        defaults={
            'email': 'analyst@example.com',
            'role': 'analyst'
        }
    )
    if created:
        analyst_user.set_password('analyst123')
        analyst_user.save()

def create_categories():
    print('Creating categories...')
    
    categories_data = [
        {'name': 'Elektronik', 'code': 'ELK', 'description': 'Perangkat elektronik'},
        {'name': 'Peralatan Dapur', 'code': 'DKP', 'description': 'Peralatan untuk dapur'},
        {'name': 'Furniture', 'code': 'FRT', 'description': 'Perabot rumah tangga'},
        {'name': 'Otomotif', 'code': 'OTO', 'description': 'Sparepart dan aksesori otomotif'},
        {'name': 'Peralatan Kantor', 'code': 'KTR', 'description': 'Peralatan untuk kantor'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            code=cat_data['code'],
            defaults={
                'description': cat_data['description']
            }
        )
        categories.append(category)
    
    return categories


def create_customers():
    print('Creating customers...')
    
    customers_data = [
        {'name': 'Toko Serba Ada', 'phone': '021-11111111', 'email': 'toko@serbaada.com', 'address': 'Jl. Raya Kebayoran No. 1, Jakarta'},
        {'name': 'Warung Bu Siti', 'phone': '021-22222222', 'email': 'warung@siti.com', 'address': 'Jl. Diponegoro No. 23, Bandung'},
        {'name': 'Toko Bangunan Jaya', 'phone': '021-33333333', 'email': 'bangunan@jaya.com', 'address': 'Jl. Ahmad Yani No. 45, Surabaya'},
        {'name': 'Restoran Sari Rasa', 'phone': '021-44444444', 'email': 'restoran@sarirasa.com', 'address': 'Jl. Thamrin No. 56, Medan'},
        {'name': 'Kantor Pemerintahan', 'phone': '021-55555555', 'email': 'kantor@gov.id', 'address': 'Jl. Veteran No. 67, Makassar'},
    ]
    
    for cust_data in customers_data:
        Customer.objects.get_or_create(
            name=cust_data['name'],
            defaults={
                'phone': cust_data['phone'],
                'email': cust_data['email'],
                'address': cust_data['address']
            }
        )

def create_products():
    print('Creating products...')
    
    # Get categories
    categories = list(Category.objects.all())
    
    products_data = [
        {'sku': 'ELK-001', 'name': 'Laptop Gaming', 'category': categories[0] if categories else None, 'uom': 'PCS', 'min_stock': 5, 'price': Decimal('15000000')},
        {'sku': 'ELK-002', 'name': 'Smartphone', 'category': categories[0] if categories else None, 'uom': 'PCS', 'min_stock': 10, 'price': Decimal('5000000')},
        {'sku': 'ELK-003', 'name': 'Kabel USB', 'category': categories[0] if categories else None, 'uom': 'PCS', 'min_stock': 20, 'price': Decimal('50000')},
        {'sku': 'DKP-001', 'name': 'Rice Cooker', 'category': categories[1] if categories else None, 'uom': 'PCS', 'min_stock': 8, 'price': Decimal('400000')},
        {'sku': 'DKP-002', 'name': 'Blender', 'category': categories[1] if categories else None, 'uom': 'PCS', 'min_stock': 6, 'price': Decimal('300000')},
        {'sku': 'DKP-003', 'name': 'Panci Stainless', 'category': categories[1] if categories else None, 'uom': 'PCS', 'min_stock': 12, 'price': Decimal('250000')},
        {'sku': 'FRT-001', 'name': 'Kursi Kantor', 'category': categories[2] if categories else None, 'uom': 'PCS', 'min_stock': 3, 'price': Decimal('800000')},
        {'sku': 'FRT-002', 'name': 'Meja Makan', 'category': categories[2] if categories else None, 'uom': 'PCS', 'min_stock': 2, 'price': Decimal('2000000')},
        {'sku': 'OTO-001', 'name': 'Oli Mesin', 'category': categories[3] if categories else None, 'uom': 'LTR', 'min_stock': 15, 'price': Decimal('55000')},
        {'sku': 'KTR-001', 'name': 'Kertas A4', 'category': categories[4] if categories else None, 'uom': 'REAM', 'min_stock': 25, 'price': Decimal('60000')},
        {'sku': 'KTR-002', 'name': 'Pensil', 'category': categories[4] if categories else None, 'uom': 'DOZ', 'min_stock': 50, 'price': Decimal('3000')},
        {'sku': 'KTR-003', 'name': 'Penghapus', 'category': categories[4] if categories else None, 'uom': 'DOZ', 'min_stock': 30, 'price': Decimal('2000')},
    ]
    
    for prod_data in products_data:
        Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults={
                'name': prod_data['name'],
                'category': prod_data['category'],
                'uom': prod_data['uom'],
                'min_stock': prod_data['min_stock'],
                'price': prod_data['price']
            }
        )

def create_warehouses():
    print('Creating warehouses...')
    
    warehouses_data = [
        {'code': 'WH-TKO', 'name': 'Toko Electric', 'address': 'Jl. Raya Toko Electric No. 1'},
    ]
    
    for wh_data in warehouses_data:
        Warehouse.objects.get_or_create(
            code=wh_data['code'],
            defaults={
                'name': wh_data['name'],
                'address': wh_data['address']
            }
        )

def create_stock():
    print('Creating stock...')
    
    products = list(Product.objects.all())
    warehouses = list(Warehouse.objects.all())
    
    for product in products:
        for warehouse in warehouses:
            # Random stock quantity between min_stock and 3x min_stock
            min_stock = product.min_stock
            qty = random.randint(min_stock, min_stock * 3)
            
            Stock.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={'qty': qty}
            )

def create_reorder_policies():
    print('Creating reorder policies...')
    
    products = list(Product.objects.all())
    warehouses = list(Warehouse.objects.all())
    
    for product in products:
        for warehouse in warehouses:
            # Create reorder policy with random values
            avg_daily_demand = Decimal(str(random.uniform(2.0, 10.0)))
            lead_time_days = Decimal(str(random.uniform(3.0, 7.0)))
            demand_std = Decimal(str(random.uniform(1.0, 5.0)))
            
            # Calculate ROP and safety stock
            safety_stock = Decimal(str(1.65 * float(demand_std) * (float(lead_time_days) ** 0.5)))  # Z=1.65 for 95% service level
            rop = avg_daily_demand * lead_time_days + safety_stock
            reorder_qty = random.randint(10, 30)
            
            ReorderPolicy.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={
                    'avg_daily_demand': avg_daily_demand,
                    'lead_time_days': lead_time_days,
                    'service_level': Decimal('95.00'),
                    'demand_std': demand_std,
                    'safety_stock': int(safety_stock),
                    'rop': int(rop),
                    'reorder_qty': reorder_qty
                }
            )

def create_purchase_orders():
    print('Creating purchase orders...')
    
    products = list(Product.objects.all())
    warehouses = list(Warehouse.objects.all())
    
    # Create some purchase orders
    for i in range(5):
        warehouse = random.choice(warehouses)
        
        po, created = PurchaseOrder.objects.get_or_create(
            po_number=f'PO-{i+1:04d}',
            defaults={
                'warehouse': warehouse,
                'status': 'SENT' if i < 3 else 'DRAFT'
            }
        )
        
        # Add items to the PO
        total_amount = Decimal('0')
        for j in range(random.randint(2, 5)):
            product = random.choice(products)
            qty = random.randint(10, 50)
            price = product.price * Decimal(str(random.uniform(0.8, 0.95)))  # Slightly lower price than retail
            
            po_item, created = POItem.objects.get_or_create(
                purchase_order=po,
                product=product,
                defaults={
                    'qty': qty,
                    'price': price
                }
            )
            
            total_amount += qty * price
        
        po.total_amount = total_amount
        po.save()
        
        # Create goods receipt for some POs if status is SENT
        if po.status == 'SENT':
            grn, created = GoodsReceipt.objects.get_or_create(
                grn_number=f'GRN-{i+1:04d}',
                defaults={
                    'purchase_order': po,
                    'warehouse': warehouse
                }
            )

def create_sales():
    print('Creating sales...')
    
    products = list(Product.objects.all())
    customers = list(Customer.objects.all())
    warehouses = list(Warehouse.objects.all())
    
    # Create some sales
    for i in range(10):
        customer = random.choice(customers) if customers else None
        warehouse = random.choice(warehouses)
        
        sale, created = Sale.objects.get_or_create(
            invoice_number=f'INV-{i+1:06d}',
            defaults={
                'customer': customer,
                'warehouse': warehouse,
                'status': 'PAID' if i < 8 else 'DRAFT'
            }
        )
        
        # Add items to the sale
        total_amount = Decimal('0')
        for j in range(random.randint(1, 4)):
            product = random.choice(products)
            qty = random.randint(1, 5)
            price = product.price  # Use retail price
            
            sale_item, created = SaleItem.objects.get_or_create(
                sale=sale,
                product=product,
                defaults={
                    'qty': qty,
                    'price': price
                }
            )
            
            total_amount += qty * price
        
        sale.total_amount = total_amount
        sale.save()

def create_association_rules():
    print('Creating association rules...')
    
    # Create some dummy association rules
    rules_data = [
        {'antecedent': ['Rice Cooker', 'Blender'], 'consequent': ['Panci Stainless'], 'support': Decimal('0.08'), 'confidence': Decimal('0.65'), 'lift': Decimal('1.30')},
        {'antecedent': ['Laptop Gaming'], 'consequent': ['Kabel USB'], 'support': Decimal('0.12'), 'confidence': Decimal('0.70'), 'lift': Decimal('1.25')},
        {'antecedent': ['Oli Mesin'], 'consequent': ['Panci Stainless'], 'support': Decimal('0.05'), 'confidence': Decimal('0.55'), 'lift': Decimal('1.10')},
        {'antecedent': ['Kertas A4'], 'consequent': ['Pensil'], 'support': Decimal('0.15'), 'confidence': Decimal('0.75'), 'lift': Decimal('1.40')},
        {'antecedent': ['Kursi Kantor'], 'consequent': ['Meja Makan'], 'support': Decimal('0.03'), 'confidence': Decimal('0.60'), 'lift': Decimal('1.15')},
    ]
    
    for rule_data in rules_data:
        AssociationRule.objects.get_or_create(
            antecedent=rule_data['antecedent'],
            consequent=rule_data['consequent'],
            defaults={
                'support': rule_data['support'],
                'confidence': rule_data['confidence'],
                'lift': rule_data['lift']
            }
        )

if __name__ == '__main__':
    print('Starting to populate database with dummy data...')
    
    # Create users with different roles
    create_users()
    
    # Create master data
    create_categories()
    create_customers()
    create_products()
    create_warehouses()
    
    # Create inventory data
    create_stock()
    create_reorder_policies()
    
    # Create purchasing data
    create_purchase_orders()
    
    # Create sales data
    create_sales()
    
    # Create mining data (Association Rules)
    create_association_rules()
    
    print('Successfully populated database with dummy data!')