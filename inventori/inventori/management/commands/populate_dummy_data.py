from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from master.models import Category, Product, Supplier, Customer
from inventory.models import Warehouse, Stock, ReorderPolicy
from sales.models import Sale, SaleItem
from purchases.models import PurchaseOrder, POItem, GoodsReceipt
from mining.models import AssociationRule
from django.utils import timezone
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate database with dummy data...')
        
        # Create users with different roles
        self.create_users()
        
        # Create master data
        self.create_categories()
        self.create_suppliers()
        self.create_customers()
        self.create_products()
        self.create_warehouses()
        
        # Create inventory data
        self.create_stock()
        self.create_reorder_policies()
        
        # Create purchasing data
        self.create_purchase_orders()
        
        # Create sales data
        self.create_sales()
        
        # Create mining data (Association Rules)
        self.create_association_rules()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with dummy data!')
        )

    def create_users(self):
        self.stdout.write('Creating users...')
        
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin',
            is_staff=True
        )
        
        # Create manager user
        manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='manager123',
            role='manager'
        )
        
        # Create cashier user
        cashier_user = User.objects.create_user(
            username='cashier',
            email='cashier@example.com',
            password='cashier123',
            role='cashier'
        )
        
        # Create warehouse user
        warehouse_user = User.objects.create_user(
            username='warehouse',
            email='warehouse@example.com',
            password='warehouse123',
            role='warehouse'
        )
        
        # Create analyst user
        analyst_user = User.objects.create_user(
            username='analyst',
            email='analyst@example.com',
            password='analyst123',
            role='analyst'
        )

    def create_categories(self):
        self.stdout.write('Creating categories...')
        
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

    def create_suppliers(self):
        self.stdout.write('Creating suppliers...')
        
        suppliers_data = [
            {'name': 'PT. Elektronik Maju Jaya', 'contact': 'Budi Santoso', 'phone': '021-12345678', 'email': 'budi@emajujaya.com', 'address': 'Jl. Merdeka No. 123, Jakarta'},
            {'name': 'CV. Dapur Sejahtera', 'contact': 'Siti Rahayu', 'phone': '021-87654321', 'email': 'siti@dapursejahtera.com', 'address': 'Jl. Sudirman No. 45, Bandung'},
            {'name': 'PT. Furniture Indah', 'contact': 'Ahmad Priyanto', 'phone': '021-23456789', 'email': 'ahmad@furnitureindah.com', 'address': 'Jl. Gatot Subroto No. 67, Surabaya'},
            {'name': 'CV. Otomotif Makmur', 'contact': 'Rudi Hartono', 'phone': '021-98765432', 'email': 'rudi@otomotifmakmur.com', 'address': 'Jl. MT Haryono No. 89, Medan'},
            {'name': 'PT. Kantor Lestari', 'contact': 'Dewi Kusumawardhani', 'phone': '021-34567890', 'email': 'dewi@kantorlestari.com', 'address': 'Jl. Thamrin No. 101, Makassar'},
        ]
        
        for supp_data in suppliers_data:
            Supplier.objects.get_or_create(
                name=supp_data['name'],
                defaults={
                    'contact': supp_data['contact'],
                    'phone': supp_data['phone'],
                    'email': supp_data['email'],
                    'address': supp_data['address']
                }
            )

    def create_customers(self):
        self.stdout.write('Creating customers...')
        
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

    def create_products(self):
        self.stdout.write('Creating products...')
        
        # Get categories and suppliers
        categories = list(Category.objects.all())
        suppliers = list(Supplier.objects.all())
        
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

    def create_warehouses(self):
        self.stdout.write('Creating warehouses...')
        
        warehouses_data = [
            {'code': 'WH-JKT', 'name': 'Gudang Jakarta', 'address': 'Jl. Industri No. 1, Jakarta'},
            {'code': 'WH-BDG', 'name': 'Gudang Bandung', 'address': 'Jl. Pabrik No. 2, Bandung'},
            {'code': 'WH-SBY', 'name': 'Gudang Surabaya', 'address': 'Jl. Perdagangan No. 3, Surabaya'},
        ]
        
        for wh_data in warehouses_data:
            Warehouse.objects.get_or_create(
                code=wh_data['code'],
                defaults={
                    'name': wh_data['name'],
                    'address': wh_data['address']
                }
            )

    def create_stock(self):
        self.stdout.write('Creating stock...')
        
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

    def create_reorder_policies(self):
        self.stdout.write('Creating reorder policies...')
        
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

    def create_purchase_orders(self):
        self.stdout.write('Creating purchase orders...')
        
        products = list(Product.objects.all())
        suppliers = list(Supplier.objects.all())
        warehouses = list(Warehouse.objects.all())
        
        # Create some purchase orders
        for i in range(5):
            supplier = random.choice(suppliers)
            warehouse = random.choice(warehouses)
            
            po, created = PurchaseOrder.objects.get_or_create(
                po_number=f'PO-{i+1:04d}',
                defaults={
                    'supplier': supplier,
                    'warehouse': warehouse,
                    'status': 'SENT' if i < 3 else 'DRAFT'
                }
            )
            
            # Add items to the PO
            for j in range(random.randint(2, 5)):
                product = random.choice(products)
                qty = random.randint(10, 50)
                price = product.price * Decimal(str(random.uniform(0.8, 0.95)))  # Slightly lower price than retail
                
                POItem.objects.get_or_create(
                    purchase_order=po,
                    product=product,
                    defaults={
                        'qty': qty,
                        'price': price
                    }
                )
                
                po.total_amount += qty * price
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

    def create_sales(self):
        self.stdout.write('Creating sales...')
        
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

    def create_association_rules(self):
        self.stdout.write('Creating association rules...')
        
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