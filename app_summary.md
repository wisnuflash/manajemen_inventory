Aplikasi Manajemen Inventori + POS + Optimasi Inventori (Apriori) dengan Dashboard

Stack: Django 5, Bootstrap 5, MySQL, Chart.js (visualisasi).

1. Ringkasan & Tujuan

Tujuan: Mengelola data master inventori, transaksi POS (Point of Sale), pembelian (PO/GRN), pergerakan stok, dan optimasi inventori melalui association rules (Apriori) untuk rekomendasi bundling/penataan produk serta masukan pengadaan (ROP).

Output kunci:

Dashboard KPI (Penjualan hari/minggu/bulan, Nilai persediaan, Stok rendah, Alert ROP).

Top frequent itemsets & rules (support, confidence, lift).

Rekomendasi reorder (ROP + safety stock) dan cross-sell.

2. Arsitektur Aplikasi
inventori/ (root Django project)
├─ inventori/                # config (settings/urls/wsgi/asgi)
├─ accounts/                 # auth, role, permission (Django Groups)
├─ master/                   # Category, Product, Supplier, Customer
├─ inventory/                # Warehouse, Stock, StockMove, ReorderPolicy
├─ sales/                    # Sale, SaleItem (POS)
├─ purchases/                # PurchaseOrder, POItem, GoodsReceipt
├─ mining/                   # Apriori: dataset builder, rules, historis
├─ summary/                  # Dashboard KPI & laporan ringkas
└─ static/, templates/       # Bootstrap UI & aset


Pola arsitektur: MVC Django (+ service layer untuk perhitungan KPI & Apriori).
Integrasi:

POS menulis Sale + SaleItem → StockMove → update Stock.

Pembelian: PO → GoodsReceipt → StockMove (masuk).

Mining membaca dataset transaksi (basket dari SaleItem) → Apriori → simpan AssociationRule.

Dashboard membaca KPI + tabel ringkasan + chart Top Products & Top Rules.

3. Modul & Fitur
3.1 accounts

Login/Logout, Group Role: Admin, Manager, Warehouse, Cashier, Analyst.

Permission per view (Django Permission/Group).

3.2 master

CRUD: Category, Product, Supplier, Customer.

Product.min_stock, Product.price (harga retail).

3.3 inventory

Warehouse, Stock (unik per product+warehouse), StockMove (jejak audit pergerakan).

ReorderPolicy (ROP, safety stock, reorder qty).

Service: kalkulasi ROP dan Safety Stock.

3.4 sales (POS)

Sale (header) & SaleItem (detail).

Status: DRAFT → PAID/CANCELLED.

Cetak struk sederhana, shortcut barcode/sku.

3.5 purchases

PurchaseOrder (PO) & POItem.

GoodsReceipt (GRN) selaras dengan PO (opsional) → stok masuk.

3.6 mining (Apriori)

Builder basket transaksi (agregasi SaleItem per Sale).

Eksekusi Apriori → simpan frequent itemsets & association rules.

Parameter: min_support, min_confidence, filter lift >= 1.

3.7 summary (Dashboard)

KPI: penjualan (hari/minggu/bulan), nilai persediaan.

Tabel: Stok rendah, Alert ROP, PO terbuka.

Chart: Top Produk (qty/revenue), Top Rules (lift/confidence).

4. Skema Basis Data (MySQL)

Ringkasan tabel inti (tipe disederhanakan). Gunakan InnoDB & utf8mb4.

-- MASTER
CREATE TABLE category (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  code VARCHAR(30) UNIQUE,
  description VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE product (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  sku VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(150) NOT NULL,
  category_id BIGINT UNSIGNED,
  uom VARCHAR(20) DEFAULT 'PCS',
  min_stock INT UNSIGNED DEFAULT 0,
  price DECIMAL(12,2) NOT NULL DEFAULT 0,
  is_active TINYINT(1) DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES category(id)
) ENGINE=InnoDB;

CREATE TABLE supplier (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(150) NOT NULL,
  contact VARCHAR(100), phone VARCHAR(30), email VARCHAR(100), address VARCHAR(255),
  is_active TINYINT(1) DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE customer (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(150) NOT NULL,
  phone VARCHAR(30), email VARCHAR(100), address VARCHAR(255),
  is_active TINYINT(1) DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- WAREHOUSE & STOCK
CREATE TABLE warehouse (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  address VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE stock (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT UNSIGNED NOT NULL,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  qty INT NOT NULL DEFAULT 0,
  UNIQUE KEY uq_stock (product_id, warehouse_id),
  FOREIGN KEY (product_id) REFERENCES product(id),
  FOREIGN KEY (warehouse_id) REFERENCES warehouse(id)
) ENGINE=InnoDB;

CREATE TABLE stock_move (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT UNSIGNED NOT NULL,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  ref_type ENUM('SALE','GRN','ADJUST','TRANSFER') NOT NULL,
  ref_id BIGINT UNSIGNED,
  qty_in INT NOT NULL DEFAULT 0,
  qty_out INT NOT NULL DEFAULT 0,
  note VARCHAR(255),
  moved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_sm_ref (ref_type, ref_id),
  INDEX idx_sm_product_date (product_id, moved_at),
  FOREIGN KEY (product_id) REFERENCES product(id),
  FOREIGN KEY (warehouse_id) REFERENCES warehouse(id)
) ENGINE=InnoDB;

-- REPLENISHMENT (ROP)
CREATE TABLE reorder_policy (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT UNSIGNED NOT NULL,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  avg_daily_demand DECIMAL(10,2) DEFAULT 0,
  lead_time_days DECIMAL(10,2) DEFAULT 0,
  service_level DECIMAL(5,2) DEFAULT 95.00,
  demand_std DECIMAL(10,2) DEFAULT 0,
  rop INT DEFAULT 0,
  safety_stock INT DEFAULT 0,
  reorder_qty INT DEFAULT 0,
  UNIQUE KEY uq_policy (product_id, warehouse_id),
  FOREIGN KEY (product_id) REFERENCES product(id),
  FOREIGN KEY (warehouse_id) REFERENCES warehouse(id)
) ENGINE=InnoDB;

-- PURCHASES
CREATE TABLE purchase_order (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  po_number VARCHAR(40) UNIQUE NOT NULL,
  supplier_id BIGINT UNSIGNED NOT NULL,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  status ENUM('DRAFT','SENT','RECEIVED','CANCELLED') DEFAULT 'DRAFT',
  total_amount DECIMAL(14,2) DEFAULT 0,
  ordered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (supplier_id) REFERENCES supplier(id),
  FOREIGN KEY (warehouse_id) REFERENCES warehouse(id)
) ENGINE=InnoDB;

CREATE TABLE po_item (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  purchase_order_id BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  qty INT NOT NULL,
  price DECIMAL(12,2) NOT NULL,
  FOREIGN KEY (purchase_order_id) REFERENCES purchase_order(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES product(id)
) ENGINE=InnoDB;

CREATE TABLE goods_receipt (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  purchase_order_id BIGINT UNSIGNED,
  grn_number VARCHAR(40) UNIQUE NOT NULL,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (purchase_order_id) REFERENCES purchase_order(id),
  FOREIGN KEY (warehouse_id) REFERENCES warehouse(id)
) ENGINE=InnoDB;

-- SALES (POS)
CREATE TABLE sale (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  invoice_number VARCHAR(40) UNIQUE NOT NULL,
  customer_id BIGINT UNSIGNED,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  status ENUM('DRAFT','PAID','CANCELLED') DEFAULT 'DRAFT',
  total_amount DECIMAL(14,2) DEFAULT 0,
  sold_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customer(id),
  FOREIGN KEY (warehouse_id) REFERENCES warehouse(id)
) ENGINE=InnoDB;

CREATE TABLE sale_item (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  sale_id BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  qty INT NOT NULL,
  price DECIMAL(12,2) NOT NULL,
  FOREIGN KEY (sale_id) REFERENCES sale(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES product(id)
) ENGINE=InnoDB;

-- MINING (Apriori)
CREATE TABLE association_rule (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  antecedent JSON NOT NULL,   -- contoh: ["Stopkontak","Saklar"]
  consequent JSON NOT NULL,   -- contoh: ["Dudukan Lampu"]
  support DECIMAL(6,4) NOT NULL,
  confidence DECIMAL(6,4) NOT NULL,
  lift DECIMAL(8,4) NOT NULL,
  generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_rule_metrics (lift, confidence, support)
) ENGINE=InnoDB;

5. Alur Bisnis Utama
5.1 POS (Penjualan)

Kasir pilih gudang → scan SKU → tambah SaleItem.

Klik Bayar → Sale.status = PAID.

Tuliskan StockMove(ref_type='SALE', qty_out) & update Stock.

Update Sale.total_amount = Σ(qty * price).

5.2 Pembelian

Buat PO → POItem.

Saat barang datang → GRN (GoodsReceipt) → StockMove(ref_type='GRN', qty_in).

Update Stock.qty += qty_in, status PO → RECEIVED.

5.3 Optimasi (Apriori + ROP)

Builder Basket: group SaleItem per Sale.id.

Jalankan Apriori → rules (support/confidence/lift).

Gunakan rules untuk:

Cross-sell / bundling (UI POS: rekomendasi item ketika men-scan).

Planogram (penataan barang berdekatan).

Kebijakan Reorder (terpisah):

Hitung avg_daily_demand, lead_time_days, demand_std.

Safety Stock = z * σ_d * sqrt(LT).

ROP = d_avg * LT + SS.

Alert ketika Stock.qty <= ROP.

6. API & URL (Django)

master/ (CRUD): /products/, /categories/, /suppliers/, /customers/

sales/:

GET /pos/ (form POS)

POST /pos/add-item/ (ajax)

POST /pos/pay/

purchases/: /po/, /grn/

inventory/: /stocks/, /moves/, /reorder/

mining/:

POST /mining/run/ (generate rules; param: min_support, min_confidence)

GET /mining/rules/ (list & filter by lift/confidence)

summary/: /summary/ (dashboard)

GET /summary/api/top-products/ (JSON untuk chart)

GET /summary/api/top-rules/ (JSON untuk chart)

7. Dashboard (KPI & Visual)

KPI Cards

Penjualan hari ini, minggu ini, bulan ini (sum Sale.total_amount status PAID).

Nilai persediaan Σ(Stock.qty * Product.price) (bisa diganti average cost).

Tabel

Stok Rendah: Stock.qty <= Product.min_stock.

Alert ROP: gabung Stock + ReorderPolicy, tampilkan qty, ROP, reorder_qty.

PO Terbuka: PurchaseOrder.status in (DRAFT,SENT).

Chart

Top Produk (Qty) bulan berjalan.

Top Rules (urut lift atau confidence) — antec → cons.

8. Algoritma Apriori (Ringkas)

Parameter:

min_support (rasio transaksi berisi itemset, mis. 0.05)

min_confidence (mis. 0.6), lift >= 1 (positif korelasi)

Pseudocode:

1. Bangun dataset: transaksi = {sale_id: {sku1, sku2, ...}}
2. Generate frequent 1-itemsets (support >= min_support)
3. k = 2
4. Loop:
   a. Candidate Ck = kombinasi join dari L(k-1)
   b. Hitung support(Ck) lewat scan transaksi
   c. Lk = { c in Ck | support(c) >= min_support }
   d. Jika Lk kosong → stop
   e. k = k + 1
5. Bangun rules dari frequent itemsets:
   Untuk setiap frequent itemset F dan subset non-kosong A ⊂ F:
     B = F \ A
     confidence(A→B) = support(F) / support(A)
     lift(A→B) = confidence / support(B)
     Jika confidence >= min_confidence dan lift >= 1 → simpan rule


Integrasi UI POS:

Saat item A ditambahkan:

Ambil rules dengan antecedent mengandung A (atau subset dari keranjang saat ini).

Urutkan berdasarkan lift → tampilkan rekomendasi (B).

9. Perhitungan ROP & Safety Stock

Safety Stock (SS): SS = z * σ_d * sqrt(LT)
(z ditentukan oleh service level: 90% ~ 1.28, 95% ~ 1.65, 97.5% ~ 1.96)

ROP: ROP = d_avg * LT + SS

Reorder Qty: opsi EOQ atau fixed lot (mis. kelipatan dus).

Scheduler (opsional Celery/CRON):

Recompute kebijakan ROP bulanan / mingguan.

Kirim notifikasi ketika qty <= ROP.

10. Indexing & Performa

Index penting:

sale(sold_at, status), sale_item(sale_id, product_id).

stock(product_id, warehouse_id) UNIQUE.

stock_move(product_id, moved_at).

reorder_policy(product_id, warehouse_id) UNIQUE.

association_rule(lift, confidence, support) (sorting cepat).

Materialized table agregasi penjualan harian (opsional) untuk laporan cepat.

11. Role & Permission
Role	Akses Utama
Admin	Full access
Manager	CRUD master, laporan, set ROP, jalankan mining
Warehouse	GRN, transfer, adjustment
Cashier	POS (buat & bayar penjualan)
Analyst	Read-only data, lihat dashboard & hasil mining
12. Validasi & Pengujian

Black-box (contoh):

POS: tambah item → total berubah benar; bayar → stok berkurang; pembatalan → rollback.

GRN: terima barang → stok bertambah; referensi ke PO konsisten.

Mining: ganti min_support/min_confidence → jumlah rules berubah; nilai support/confidence akurat.

ROP: ketika qty <= ROP → muncul alert; recompute mengubah nilai sesuai parameter.

Load Test (opsional):

Banyak transaksi per hari → dashboard dan query KPI tetap <300ms (dengan index/materialized agg).

13. Konfigurasi & Deployment

ENV:

MYSQL_HOST, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD, DJANGO_SECRET_KEY, DEBUG.

Static: gunakan CDN Bootstrap + collectstatic untuk aset lokal.

Backup: dump MySQL, snapshot rules & kebijakan ROP.

Security: enforce login, limit akses KPI nilai persediaan ke Manager/Admin.

14. Contoh Endpoint JSON
GET /summary/api/top-products/?period=month
→ 200 [{ "product__sku": "SK-001", "product__name": "Stopkontak", "qty": 120, "revenue": 7200000 }, ...]

GET /mining/rules/?sort=lift&limit=10
→ 200 [{ "antecedent": ["Stopkontak"], "consequent": ["Saklar"], "support": 0.08, "confidence": 0.65, "lift": 1.25 }, ...]

15. Checklist Implementasi

 Buat project & app sesuai struktur.

 Implementasi models & migrasi MySQL.

 CRUD master (Product, Category, Supplier, Customer).

 POS page (scan SKU, tambah item, bayar).

 PO & GRN.

 StockMove terhubung semua transaksi.

 ReorderPolicy + service perhitungan ROP.

 Mining Apriori (builder dataset + executor + simpan rules).

 Dashboard KPI + chart + tabel.

 Permission per role.

 Seeder data demo (opsional).

 Export PDF/Excel (opsional).

16. Catatan Implementasi Django (Singkat)

Tambahkan summary, mining, inventory, sales, purchases, master, accounts ke INSTALLED_APPS.

Gunakan crispy-forms + bootstrap5 untuk form CRUD.

Chart.js lewat CDN.

Query berat pakai .select_related()/.prefetch_related().

17. Lampiran: Contoh Integrasi Apriori (Python, ringkas)
# mining/services.py (contoh ringkas)
from collections import defaultdict
from django.db import transaction
from sales.models import SaleItem
from .models import AssociationRule

def build_baskets():
    baskets = defaultdict(set)
    for si in SaleItem.objects.select_related("sale", "product").values("sale_id", "product__sku"):
        baskets[si["sale_id"]].add(si["product__sku"])
    return list(baskets.values())

def apriori(baskets, min_support=0.05, min_conf=0.6):
    from itertools import combinations
    N = len(baskets)
    def support(itemset):
        c = sum(1 for b in baskets if itemset.issubset(b))
        return c / N

    # L1
    items = sorted({i for b in baskets for i in b})
    L = [{frozenset([i]) for i in items if support({i}) >= min_support}]
    k = 2
    while L[-1]:
        Ck = set()
        prev = list(L[-1])
        for a in range(len(prev)):
            for b in range(a+1, len(prev)):
                union = prev[a] | prev[b]
                if len(union) == k:
                    Ck.add(union)
        Lk = {c for c in Ck if support(c) >= min_support}
        if not Lk: break
        L.append(Lk); k += 1

    # Rules
    rules = []
    for Lk in L[1:]:
        for F in Lk:
            for r in range(1, len(F)):
                for A in combinations(F, r):
                    A, B = set(A), set(F) - set(A)
                    supF = support(F)
                    supA = support(A)
                    supB = support(B)
                    conf = supF / supA if supA else 0
                    lift = conf / supB if supB else 0
                    if conf >= min_conf and lift >= 1:
                        rules.append((list(A), list(B), supF, conf, lift))
    return rules

def run_and_persist(min_support=0.05, min_conf=0.6, limit=200):
    baskets = build_baskets()
    rules = apriori(baskets, min_support, min_conf)
    rules.sort(key=lambda x: (-x[4], -x[3], -x[2]))  # by lift, confidence, support
    with transaction.atomic():
        AssociationRule.objects.all().delete()
        for a, b, sup, conf, lift in rules[:limit]:
            AssociationRule.objects.create(
                antecedent=a, consequent=b, support=sup, confidence=conf, lift=lift
            )

18. Glosarium

Apriori: algoritma untuk menambang pola itemset sering muncul bersama pada transaksi.

Support: proporsi transaksi yang memuat itemset.

Confidence: probabilitas konsekuen terjadi jika antecedent terjadi.

Lift: kekuatan asosiasi relatif; > 1 berarti korelasi positif.

ROP (Reorder Point): titik pemesanan ulang agar tidak stockout selama lead time.

Safety Stock: persediaan pengaman menghadapi variabilitas permintaan/lead time.