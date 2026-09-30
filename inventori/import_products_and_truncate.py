#!/usr/bin/env python
"""
Script to:
1. Backup db.sqlite3
2. Truncate all non-user / non-rbac data
3. Create Categories
4. Import products from 'DATA BARANG TERBARU new.xlsx' into product table with category mapping
"""

import os
import sys
import shutil
import re
from decimal import Decimal
import openpyxl
import django

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventori.settings')
django.setup()

from django.db import connection, transaction
from master.models import Product, Category, Customer
from inventory.models import Warehouse, Stock, StockMove, ReorderPolicy
from sales.models import Sale, SaleItem
from purchases.models import PurchaseOrder, POItem, GoodsReceipt
from mining.models import AssociationRule
from accounts.models import User

CATEGORY_RULES = [
    ('Saklar & Stop Kontak', 'SWT', 'Saklar, stop kontak, steker, outlet TV/data, dan aksesorisnya', [
        r'SAKLAR', r'STOP', r'STOPKONTAK', r'HOTEL', r'ENGKEL', r'SERI',
        r'TRIPLE', r'DIMMER', r'FRAME', r'GRID', r'OUTLET', r'\bSK\b',
        r'DATA CAT', r'CAT 5', r'CAT 6', r'TELPON', r'\bTV\b', r'STEKER', r'COLOKAN',
        r'UTIKON', r'BROCO', r'VIVACE', r'LEONA', r'NERO', r'AVATAR', r'PRECIOSA',
        r'GONEO', r'GANG', r'KAVACA', r'CAVACA', r'ARCHITEC', r'LUXMEN', r'INFINITY',
        r'INFINIRY', r'HAISEN', r'PNT-', r'SKL-', r'FRM-', r'SWT-', r'OB PANASONIC',
        r'\bAC\b'
    ]),
    ('Kabel Listrik', 'KBL', 'Kabel instalasi, NYM, NYY, NYA, kabel CCTV, dll.', [
        r'KABEL', r'NYM', r'NYY', r'NYA', r'NYAF', r'NYFGBY',
        r'ETERNA', r'LINDO', r'SUPRAME', r'SUPREME', r'EXTRANA', r'TUKUIKI', r'\bBC\b',
        r'BELDEN', r'KBL-', r'CCTV'
    ]),
    ('Lampu & Penerangan', 'LMP', 'Lampu LED, downlight, T5, T8, kap, spotlight, bohlam, dll.', [
        r'LAMPU', r'BOHLAM', r'BOLHAM', r'DOWNLIGHT', r'\bDL\b', r'PANEL', r'T5', r'T8',
        r'KAP', r'TRACK', r'FLOODLIGHT', r'LED', r'STRIP', r'LESTRIP', r'HALOGEN',
        r'HILED', r'OPPEL', r'APPOLO', r'SPOTLIGHT', r'BULB', r'PHILIPS', r'MORGEN',
        r'FITTING', r'FITING', r'DUDUKAN', r'COB', r'WATT', r'INLITE', r'OSIWA', r'HATASU',
        r'HIDEKI', r'MEGAMAN', r'KTR-', r'LMP-', r'MESON', r'DN 020B', r'HOSING'
    ]),
    ('MCB & Box Panel', 'MCB', 'MCB, ELCB, RCBO, box panel, box MCB, box KWH, dll.', [
        r'MCB', r'ELCB', r'RCBO', r'BOX', r'HAGER', r'SCHNEIDER', r'BOSS PROTINUS',
        r'PRESTO', r'VIRES', r'TVA', r'BOX KWH', r'SISIR', r'GROUP', r'PANEL SIKU',
        r'17X20X12', r'80\s*X\s*80', r'100\s*X\s*100'
    ]),
    ('Pipa & Trunking', 'PIP', 'Pipa conduit, trunking/protektor, T dus, klem, inbow doos, dll.', [
        r'PIPA', r'CONDUIT', r'CLIPSAL', r'DURADUS', r'T DUS', r'TEDUS', r'PROTEKTOR',
        r'\bTC\b', r'TRUNKING', r'KLEM', r'ELBOW', r'SOCK', r'SOK', r'SOX', r'INBOW', r'OUTBOW',
        r'KRESDUS', r'CLAM', r'PIP-', r'KLM-', r'LESO', r'\bIB\b'
    ]),
    ('Ventilasi & Exhaust', 'EXH', 'Exhaust fan, kipas angin, ventilasi udara', [
        r'HEKSOS', r'EXHAUST', r'KIPAS', r'KDK', r'MASPION', r'SEKAI'
    ]),
    ('Aksesoris & Kelistrikan', 'ACC', 'Join, skun, isolasi, travo, adaptor, arde, ties, dll.', [
        r'JOIN', r'SKUN', r'ISOLASI', r'CONNECTOR', r'TERMINAL', r'TRAVO', r'ADAPTOR',
        r'SOLASI', r'NITO', r'HIMEL', r'SPIT', r'SEAL TAPE', r'ARDE', r'GROUNDING',
        r'SELCON', r'PHOTOCELL', r'TIMER', r'FUSE', r'SEKERING', r'BEL', r'BELL',
        r'SKN-', r'JON-', r'TRV-', r'TISE', r'VINIL', r'VNL-', r'KUKU MACAN', r'KKM-',
        r'OSKA'
    ]),
]

def backup_database():
    db_path = os.path.join(BASE_DIR, 'db.sqlite3')
    backup_path = os.path.join(BASE_DIR, 'db.sqlite3.bak')
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to {backup_path}")

def truncate_data():
    print("Truncating tables (preserving User & RBAC)...")
    tables_to_truncate = [
        'sale_item',
        'sale',
        'po_item',
        'goods_receipt',
        'purchase_order',
        'stock_move',
        'stock',
        'reorder_policy',
        'association_rule',
        'product',
        'category',
        'customer',
        'warehouse',
        'django_admin_log',
    ]
    
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF;")
        for table in tables_to_truncate:
            cursor.execute(f'DELETE FROM "{table}";')
            print(f" - Table {table} cleared.")
        
        quoted_tables = ", ".join(f"'{t}'" for t in tables_to_truncate)
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name IN ({quoted_tables});")
        cursor.execute("PRAGMA foreign_keys = ON;")
    print("All specified tables truncated successfully.\n")

def create_categories():
    print("Creating Categories...")
    category_map = {}
    for cat_name, cat_code, desc, _ in CATEGORY_RULES:
        category, created = Category.objects.get_or_create(
            code=cat_code,
            defaults={'name': cat_name, 'description': desc}
        )
        category_map[cat_name] = category
        status = "Created" if created else "Existing"
        print(f" - [{status}] Category: {category.name} (Code: {category.code})")
    return category_map

def determine_category(name_str, sku_str, category_map):
    name_upper = name_str.upper()
    sku_upper = sku_str.upper()
    for cat_name, _, _, patterns in CATEGORY_RULES:
        for p in patterns:
            if re.search(p, name_upper) or re.search(p, sku_upper):
                return category_map[cat_name]
    # Default fallback
    return category_map['Aksesoris & Kelistrikan']

def import_products_from_excel(category_map):
    excel_path = os.path.join(BASE_DIR, 'DATA BARANG TERBARU new.xlsx')
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"File {excel_path} not found!")

    print(f"\nLoading Excel file from {excel_path}...")
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))[1:]
    
    seen_skus = {}
    products_to_create = []
    skipped_count = 0

    for idx, r in enumerate(rows, start=2):
        name = r[0]
        raw_sku = r[1]
        raw_price = r[2]

        # Skip completely empty rows
        if not name and not raw_sku and not raw_price:
            skipped_count += 1
            continue

        # Skip repeated header row
        if str(name).strip().lower() == 'nama barang' and str(raw_sku).strip().lower() == 'kode':
            print(f"Skipping redundant header at row {idx}")
            skipped_count += 1
            continue

        name_str = str(name).strip() if name is not None else f'Produk {idx}'

        # Check if SKU is missing or '-'
        was_empty_or_dash = (raw_sku is None) or (str(raw_sku).strip() in ('', '-'))

        if not was_empty_or_dash:
            base_sku = str(raw_sku).strip()
        else:
            # Generate base SKU from product name if missing in Excel
            slug = re.sub(r'[^A-Za-z0-9]+', '-', name_str).strip('-').upper()
            if not slug:
                slug = 'PRD'
            base_sku = slug[:30]

        # If SKU was empty/dash, append '-1' for the first occurrence;
        # if duplicate, increment suffix (-2, -3, etc.)
        if base_sku not in seen_skus:
            seen_skus[base_sku] = 1
            sku = base_sku if not was_empty_or_dash else f"{base_sku}-1"
        else:
            seen_skus[base_sku] += 1
            sku = f"{base_sku}-{seen_skus[base_sku]}"

        # Truncate to max_length=50 if needed
        if len(sku) > 50:
            suffix = f"-{seen_skus[base_sku]}"
            sku = sku[:50 - len(suffix)] + suffix

        # Parse price
        price = Decimal('0')
        if raw_price is not None:
            if isinstance(raw_price, (int, float)):
                price = Decimal(str(int(raw_price) if isinstance(raw_price, float) and raw_price.is_integer() else raw_price))
            else:
                cleaned_p = re.sub(r'[^0-9.]', '', str(raw_price))
                if cleaned_p:
                    try:
                        price = Decimal(cleaned_p)
                    except Exception:
                        price = Decimal('0')

        # Determine category
        cat = determine_category(name_str, sku, category_map)

        product = Product(
            sku=sku,
            name=name_str[:150],
            category=cat,
            uom='PCS',
            min_stock=0,
            price=price,
            is_active=True
        )
        products_to_create.append(product)

    print(f"Prepared {len(products_to_create)} products for insertion.")
    
    # Bulk insert
    with transaction.atomic():
        Product.objects.bulk_create(products_to_create, batch_size=500)
    
    print(f"Successfully inserted {len(products_to_create)} products into table 'product'.")

def verify():
    print("\n=== Verification ===")
    print(f"User count (accounts_user): {User.objects.count()}")
    print(f"Category count: {Category.objects.count()}")
    print(f"Product count: {Product.objects.count()}")
    
    print("\nProduct count per Category:")
    for cat in Category.objects.all():
        print(f" - {cat.name} ({cat.code}): {Product.objects.filter(category=cat).count()} produk")
    
    print("\nSample 5 Products with Categories in DB:")
    for p in Product.objects.select_related('category').all()[:5]:
        print(f" - [{p.category.name if p.category else 'No Category'}] {p.sku}: {p.name} (Rp{p.price:,.0f})")

if __name__ == '__main__':
    backup_database()
    truncate_data()
    cat_map = create_categories()
    import_products_from_excel(cat_map)
    verify()
