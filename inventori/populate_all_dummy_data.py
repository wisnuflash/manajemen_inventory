#!/usr/bin/env python
"""
Script to populate dummy data for all remaining tables:
- Warehouse
- Customer
- Stock (for all products across warehouses)
- ReorderPolicy (for all products)
- PurchaseOrder & POItem
- GoodsReceipt
- Sale & SaleItem (distributed across today, this week, this month, and past month)
- StockMove
- AssociationRule (Apriori rules with real product names)
"""

import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal
import django

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventori.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from accounts.models import User
from master.models import Product, Category, Customer
from inventory.models import Warehouse, Stock, StockMove, ReorderPolicy
from sales.models import Sale, SaleItem
from purchases.models import PurchaseOrder, POItem, GoodsReceipt
from mining.models import AssociationRule

def populate_warehouses():
    print("1. Populating Warehouses...")
    warehouses_data = [
        {'code': 'WH-TKO', 'name': 'Toko Electric (Gudang Utama)', 'address': 'Jl. Raya Toko Electric No. 1, Jakarta'},
        {'code': 'WH-GDG', 'name': 'Gudang Logistik & Transit', 'address': 'Jl. Industri Sentra No. 18, Bekasi'},
    ]
    warehouses = []
    for w_data in warehouses_data:
        w, created = Warehouse.objects.get_or_create(
            code=w_data['code'],
            defaults={'name': w_data['name'], 'address': w_data['address']}
        )
        warehouses.append(w)
        status = "Created" if created else "Existing"
        print(f"   [{status}] Warehouse: {w.name} ({w.code})")
    return warehouses

def populate_customers():
    print("\n2. Populating Customers...")
    customers_data = [
        {'name': 'PT Citra Mandiri Elektrik', 'phone': '021-5550123', 'email': 'purchasing@citramandiri.com', 'address': 'Kawasan Industri Pulogadung Blok B4, Jakarta'},
        {'name': 'CV Bintang Terang Listrik', 'phone': '021-7788990', 'email': 'order@bintangterang.co.id', 'address': 'Jl. Fatmawati Raya No. 45, Jakarta Selatan'},
        {'name': 'Toko Sinar Jaya Elektrik', 'phone': '022-4201122', 'email': 'sinarjaya@gmail.com', 'address': 'Jl. ABC No. 88, Bandung'},
        {'name': 'Kontraktor Graha Sentosa', 'phone': '021-8899123', 'email': 'logistik@grahasentosa.com', 'address': 'Jl. D.I. Panjaitan No. 12, Jakarta Timur'},
        {'name': 'PT Sumber Daya Tehnik', 'phone': '031-5678901', 'email': 'procurement@sumberdaya.com', 'address': 'Jl. Mayjen Sungkono No. 100, Surabaya'},
        {'name': 'UD Makmur Abadi', 'phone': '021-3141592', 'email': 'makmurabadi@yahoo.com', 'address': 'Pasar Kenari Mas Lantai 1 No. 24, Jakarta Pusat'},
        {'name': 'Toko Berkah Cahaya', 'phone': '0812-3456-7890', 'email': 'berkahcahaya@gmail.com', 'address': 'Jl. Raya Bogor KM 28, Depok'},
        {'name': 'Surya Kencana Listrik', 'phone': '0813-8899-0011', 'email': 'suryakencana.listrik@gmail.com', 'address': 'Jl. Pajajaran No. 34, Bogor'},
        {'name': 'Proyek Apartemen Grand Kemang', 'phone': '021-7190011', 'email': 'mep@grandkemang.co.id', 'address': 'Jl. Kemang Raya No. 10, Jakarta Selatan'},
        {'name': 'Bengkel Listrik Pratama', 'phone': '0817-1234-5678', 'email': 'pratamabengkel@gmail.com', 'address': 'Jl. Ciledug Raya No. 15, Tangerang'},
    ]
    customers = []
    for c_data in customers_data:
        c, created = Customer.objects.get_or_create(
            name=c_data['name'],
            defaults={
                'phone': c_data['phone'],
                'email': c_data['email'],
                'address': c_data['address'],
                'is_active': True
            }
        )
        customers.append(c)
    print(f"   Total {len(customers)} customers populated.")
    return customers

def populate_stock_and_reorder(warehouses):
    print("\n3. Populating Stock & Reorder Policies for Products...")
    products = list(Product.objects.all())
    if not products:
        print("   No products found! Please import products first.")
        return

    stocks_to_create = []
    reorder_to_create = []
    existing_stock_keys = set(Stock.objects.values_list('product_id', 'warehouse_id'))
    existing_reorder_keys = set(ReorderPolicy.objects.values_list('product_id', 'warehouse_id'))

    main_wh = warehouses[0]
    sec_wh = warehouses[1] if len(warehouses) > 1 else warehouses[0]

    for idx, prod in enumerate(products):
        # 1. Reorder Policy for Main Warehouse
        avg_demand = Decimal(str(round(random.uniform(1.5, 6.0), 2)))
        lead_time = Decimal(str(round(random.uniform(2.0, 5.0), 2)))
        demand_std = Decimal(str(round(random.uniform(0.5, 2.5), 2)))
        safety_stock = int(1.65 * float(demand_std) * (float(lead_time) ** 0.5))
        rop = int(float(avg_demand) * float(lead_time) + safety_stock)
        reorder_qty = random.randint(20, 80)

        if (prod.id, main_wh.id) not in existing_reorder_keys:
            reorder_to_create.append(ReorderPolicy(
                product=prod,
                warehouse=main_wh,
                avg_daily_demand=avg_demand,
                lead_time_days=lead_time,
                service_level=Decimal('95.00'),
                demand_std=demand_std,
                safety_stock=safety_stock,
                rop=rop,
                reorder_qty=reorder_qty
            ))

        # 2. Stock for Main Warehouse
        # For a few items (around 20 items), make stock below ROP to trigger low stock alerts
        if idx % 50 == 0:
            qty_main = random.randint(1, max(1, rop - 1))
        else:
            qty_main = random.randint(rop + 5, rop + 120)

        if (prod.id, main_wh.id) not in existing_stock_keys:
            stocks_to_create.append(Stock(
                product=prod,
                warehouse=main_wh,
                qty=qty_main
            ))

        # 3. Stock for Secondary Warehouse (for half of products)
        if idx % 2 == 0 and sec_wh.id != main_wh.id:
            if (prod.id, sec_wh.id) not in existing_stock_keys:
                qty_sec = random.randint(20, 200)
                stocks_to_create.append(Stock(
                    product=prod,
                    warehouse=sec_wh,
                    qty=qty_sec
                ))

    with transaction.atomic():
        if reorder_to_create:
            ReorderPolicy.objects.bulk_create(reorder_to_create, batch_size=500)
        if stocks_to_create:
            Stock.objects.bulk_create(stocks_to_create, batch_size=500)

    print(f"   Created {len(stocks_to_create)} Stock records.")
    print(f"   Created {len(reorder_to_create)} ReorderPolicy records.")

def populate_purchases(warehouses):
    print("\n4. Populating Purchase Orders & Goods Receipts...")
    products = list(Product.objects.all())
    main_wh = warehouses[0]
    
    # Clean previous POs if needed
    now = timezone.now()
    po_count = 15

    for i in range(1, po_count + 1):
        po_number = f"PO-2026-{i:04d}"
        days_ago = (po_count - i) * 3 + random.randint(0, 2)
        ordered_time = now - timedelta(days=days_ago, hours=random.randint(1, 8))

        if i <= 8:
            status = 'RECEIVED'
        elif i <= 12:
            status = 'SENT'
        else:
            status = 'DRAFT'

        po, created = PurchaseOrder.objects.get_or_create(
            po_number=po_number,
            defaults={
                'warehouse': main_wh,
                'status': status,
                'total_amount': Decimal('0')
            }
        )
        PurchaseOrder.objects.filter(id=po.id).update(ordered_at=ordered_time)

        # Add PO items
        sample_prods = random.sample(products, random.randint(3, 7))
        po_total = Decimal('0')
        po_items = []
        for p in sample_prods:
            qty = random.randint(20, 100)
            cost_price = p.price * Decimal(str(round(random.uniform(0.70, 0.85), 2)))
            if cost_price <= 0:
                cost_price = Decimal('5000')
            po_items.append(POItem(
                purchase_order=po,
                product=p,
                qty=qty,
                price=cost_price
            ))
            po_total += qty * cost_price

        POItem.objects.filter(purchase_order=po).delete()
        POItem.objects.bulk_create(po_items)
        PurchaseOrder.objects.filter(id=po.id).update(total_amount=po_total)

        # Create GoodsReceipt for RECEIVED status
        if status == 'RECEIVED':
            grn_num = f"GRN-2026-{i:04d}"
            grn_time = ordered_time + timedelta(days=random.randint(2, 4))
            grn, _ = GoodsReceipt.objects.get_or_create(
                grn_number=grn_num,
                defaults={
                    'purchase_order': po,
                    'warehouse': main_wh
                }
            )
            GoodsReceipt.objects.filter(id=grn.id).update(received_at=grn_time)

            # Record stock movement for this GRN
            for itm in po_items:
                StockMove.objects.create(
                    product=itm.product,
                    warehouse=main_wh,
                    ref_type='GRN',
                    ref_id=grn.id,
                    qty_in=itm.qty,
                    qty_out=0,
                    note=f"Penerimaan {grn_num} ({po_number})"
                )

    print(f"   Created {PurchaseOrder.objects.count()} Purchase Orders and {GoodsReceipt.objects.count()} Goods Receipts.")

def populate_sales(warehouses, customers):
    print("\n5. Populating Sales (POS transactions) across time periods...")
    products = list(Product.objects.all())
    users = list(User.objects.all())
    main_wh = warehouses[0]

    # Pre-select frequent bundles to establish realistic market basket associations
    switch_prods = list(Product.objects.filter(category__code='SWT')[:30])
    light_prods = list(Product.objects.filter(category__code='LMP')[:30])
    cable_prods = list(Product.objects.filter(category__code='KBL')[:20])
    pipe_prods = list(Product.objects.filter(category__code='PIP')[:20])
    acc_prods = list(Product.objects.filter(category__code='ACC')[:20])

    now = timezone.now()
    sales_to_generate = 75

    for i in range(1, sales_to_generate + 1):
        inv_num = f"INV-2026{i:05d}"
        
        # Distribute dates:
        # i 1-15: past month (30 - 45 days ago)
        # i 16-45: earlier this month (8 - 29 days ago)
        # i 46-65: this week (1 - 7 days ago)
        # i 66-75: today
        if i <= 15:
            days_ago = random.randint(31, 45)
        elif i <= 45:
            days_ago = random.randint(8, 29)
        elif i <= 65:
            days_ago = random.randint(1, 7)
        else:
            days_ago = 0

        sale_time = now - timedelta(days=days_ago, hours=random.randint(8, 20), minutes=random.randint(0, 59))
        cust = random.choice(customers) if random.random() > 0.15 else None
        usr = random.choice(users) if users else None
        status = 'PAID' if i <= 70 else 'DRAFT'

        sale, _ = Sale.objects.get_or_create(
            invoice_number=inv_num,
            defaults={
                'customer': cust,
                'warehouse': main_wh,
                'user': usr,
                'status': status,
                'total_amount': Decimal('0')
            }
        )
        Sale.objects.filter(id=sale.id).update(sold_at=sale_time)

        # Decide basket pattern:
        # Pattern A: Saklar + Pipe/Protector + Kabel
        # Pattern B: Lampu + Fitting/Travo + Kabel
        # Pattern C: Random mixed
        basket_type = random.choice(['A', 'B', 'C'])
        chosen_items = []
        if basket_type == 'A' and switch_prods and pipe_prods:
            chosen_items.append(random.choice(switch_prods))
            chosen_items.append(random.choice(pipe_prods))
            if cable_prods and random.random() > 0.4:
                chosen_items.append(random.choice(cable_prods))
        elif basket_type == 'B' and light_prods and acc_prods:
            chosen_items.append(random.choice(light_prods))
            chosen_items.append(random.choice(acc_prods))
            if cable_prods and random.random() > 0.5:
                chosen_items.append(random.choice(cable_prods))
        else:
            chosen_items = random.sample(products, random.randint(2, 5))

        sale_total = Decimal('0')
        sale_items = []
        for p in chosen_items:
            qty = random.randint(1, 6)
            price = p.price if p.price > 0 else Decimal('15000')
            sale_items.append(SaleItem(
                sale=sale,
                product=p,
                qty=qty,
                price=price
            ))
            sale_total += qty * price

        SaleItem.objects.filter(sale=sale).delete()
        SaleItem.objects.bulk_create(sale_items)
        Sale.objects.filter(id=sale.id).update(total_amount=sale_total)

        # If PAID, log StockMove
        if status == 'PAID':
            for itm in sale_items:
                StockMove.objects.create(
                    product=itm.product,
                    warehouse=main_wh,
                    ref_type='SALE',
                    ref_id=sale.id,
                    qty_in=0,
                    qty_out=itm.qty,
                    note=f"Penjualan {inv_num}"
                )

    print(f"   Created {Sale.objects.count()} Sales and {SaleItem.objects.count()} Sale Items.")
    print(f"   Created {StockMove.objects.count()} Stock Movements.")

def populate_association_rules():
    print("\n6. Populating Association Rules for Apriori...")
    # Find actual product names for realistic associations
    sw_sample = Product.objects.filter(category__code='SWT').first()
    pip_sample = Product.objects.filter(category__code='PIP').first()
    kbl_sample = Product.objects.filter(category__code='KBL').first()
    lmp_sample = Product.objects.filter(category__code='LMP').first()
    acc_sample = Product.objects.filter(category__code='ACC').first()
    mcb_sample = Product.objects.filter(category__code='MCB').first()

    rules_data = [
        {
            'antecedent': [sw_sample.name if sw_sample else 'STOP KONTAK BROCO GRACIO'],
            'consequent': [pip_sample.name if pip_sample else 'TC 2'],
            'support': Decimal('0.1850'),
            'confidence': Decimal('0.7420'),
            'lift': Decimal('1.6500')
        },
        {
            'antecedent': [sw_sample.name if sw_sample else 'SAKLAR ENGKEL BROCO GRACIO'],
            'consequent': [kbl_sample.name if kbl_sample else 'KABEL NYM 2X1.5'],
            'support': Decimal('0.1420'),
            'confidence': Decimal('0.6850'),
            'lift': Decimal('1.4200')
        },
        {
            'antecedent': [lmp_sample.name if lmp_sample else 'DOWNLIGHT 4"'],
            'consequent': [acc_sample.name if acc_sample else 'TRAVO DC 12V'],
            'support': Decimal('0.1150'),
            'confidence': Decimal('0.7890'),
            'lift': Decimal('1.8200')
        },
        {
            'antecedent': [mcb_sample.name if mcb_sample else 'BOX MCB 8 GROUP HAGER'],
            'consequent': [sw_sample.name if sw_sample else 'STOP KONTAK BROCO GRACIO'],
            'support': Decimal('0.0920'),
            'confidence': Decimal('0.8150'),
            'lift': Decimal('2.0500')
        },
        {
            'antecedent': [kbl_sample.name if kbl_sample else 'KABEL NYM 2X1.5', pip_sample.name if pip_sample else 'TC 2'],
            'consequent': [sw_sample.name if sw_sample else 'STOP KONTAK BROCO GRACIO'],
            'support': Decimal('0.0840'),
            'confidence': Decimal('0.8500'),
            'lift': Decimal('2.2100')
        },
        {
            'antecedent': [acc_sample.name if acc_sample else 'JOIN 6'],
            'consequent': [kbl_sample.name if kbl_sample else 'KABEL NYM 2X1.5'],
            'support': Decimal('0.0750'),
            'confidence': Decimal('0.6650'),
            'lift': Decimal('1.3500')
        },
    ]

    AssociationRule.objects.all().delete()
    for rd in rules_data:
        AssociationRule.objects.create(
            antecedent=rd['antecedent'],
            consequent=rd['consequent'],
            support=rd['support'],
            confidence=rd['confidence'],
            lift=rd['lift']
        )
    print(f"   Created {AssociationRule.objects.count()} Association Rules.")

def verify_all():
    print("\n================== FULL VERIFICATION ==================")
    print(f" • Users: {User.objects.count()}")
    print(f" • Categories: {Category.objects.count()}")
    print(f" • Products: {Product.objects.count()}")
    print(f" • Warehouses: {Warehouse.objects.count()}")
    print(f" • Customers: {Customer.objects.count()}")
    print(f" • Stock Records: {Stock.objects.count()}")
    print(f" • Reorder Policies: {ReorderPolicy.objects.count()}")
    print(f" • Purchase Orders: {PurchaseOrder.objects.count()}")
    print(f" • PO Items: {POItem.objects.count()}")
    print(f" • Goods Receipts: {GoodsReceipt.objects.count()}")
    print(f" • Sales: {Sale.objects.count()}")
    print(f" • Sale Items: {SaleItem.objects.count()}")
    print(f" • Stock Movements: {StockMove.objects.count()}")
    print(f" • Association Rules: {AssociationRule.objects.count()}")
    print("========================================================\n")

if __name__ == '__main__':
    print("Starting Dummy Data Population...")
    whs = populate_warehouses()
    custs = populate_customers()
    populate_stock_and_reorder(whs)
    populate_purchases(whs)
    populate_sales(whs, custs)
    populate_association_rules()
    verify_all()
    print("All dummy data successfully created!")
