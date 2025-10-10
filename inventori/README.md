# Aplikasi Manajemen Inventori

Aplikasi Manajemen Inventori adalah sistem informasi berbasis web yang dibangun menggunakan framework Django untuk membantu perusahaan dalam mengelola proses bisnis terkait inventory, penjualan, pembelian, dan analisis data.

## Fitur Utama

- **Manajemen Akun**: Sistem otentikasi dengan berbagai peran pengguna
- **Manajemen Master Data**: Kategori, produk, supplier, dan customer
- **Manajemen Inventori**: Pengelolaan stok barang di berbagai gudang
- **Manajemen Penjualan**: Proses point of sale dan faktur penjualan
- **Manajemen Pembelian**: Proses pemesanan dan penerimaan barang
- **Dashboard Analitik**: KPI penjualan dan rekomendasi produk
- **Analisis Data Mining**: Algoritma Apriori untuk analisis asosiasi produk

## Struktur Aplikasi

### Aplikasi `accounts`
- **Deskripsi**: Menangani otentikasi pengguna dan manajemen akun
- **Model**:
  - `User`: Model pengguna kustom dengan berbagai peran (admin, manager, warehouse, cashier, analyst)
- **Fitur**:
  - Login/logout
  - Registrasi pengguna
  - Manajemen pengguna dengan peran yang berbeda
  - Sistem hak akses berdasarkan peran

### Aplikasi `master`
- **Deskripsi**: Menangani master data utama seperti produk, kategori, supplier, dan customer
- **Model**:
  - `Category`: Kategori produk
  - `Product`: Data master produk (SKU, nama, kategori, harga, stok minimum)
  - `Supplier`: Data supplier produk
  - `Customer`: Data pelanggan
- **Fitur**:
  - Manajemen kategori produk
  - Manajemen data produk
  - Manajemen supplier
  - Manajemen customer

### Aplikasi `inventory`
- **Deskripsi**: Mengelola inventori barang, stok, dan kebijakan pengadaan
- **Model**:
  - `Warehouse`: Gudang tempat menyimpan stok
  - `Stock`: Stok produk per gudang
  - `StockMove`: Catatan historis pergerakan stok
  - `ReorderPolicy`: Kebijakan pengadaan berdasarkan analisis statistik
- **Fitur**:
  - Pengelolaan stok produk per gudang
  - Catatan historis pergerakan stok
  - Kebijakan pengadaan otomatis (ROP - Reorder Point)
  - Peringatan stok rendah

### Aplikasi `sales`
- **Deskripsi**: Proses penjualan dan point of sale
- **Model**:
  - `Sale`: Header transaksi penjualan
  - `SaleItem`: Item produk dalam transaksi penjualan
- **Fitur**:
  - Proses point of sale
  - Cetak faktur
  - Manajemen status penjualan
  - Laporan penjualan

### Aplikasi `purchases`
- **Deskripsi**: Proses pembelian dan penerimaan barang
- **Model**:
  - `PurchaseOrder`: Pesanan pembelian ke supplier
  - `POItem`: Item produk dalam pesanan pembelian
  - `GoodsReceipt`: Penerimaan barang dari supplier
- **Fitur**:
  - Pembuatan pesanan pembelian
  - Penerimaan barang dari supplier
  - Tracking status pesanan
  - Integrasi dengan inventori

### Aplikasi `mining`
- **Deskripsi**: Algoritma data mining untuk analisis asosiasi produk
- **Model**:
  - `AssociationRule`: Aturan asosiasi produk dari algoritma Apriori
- **Fitur**:
  - Analisis asosiasi produk
  - Rekomendasi produk berdasarkan pembelian
  - Visualisasi aturan asosiasi

### Aplikasi `summary`
- **Deskripsi**: Dashboard utama dan laporan analitik
- **Fitur**:
  - Dashboard KPI (penjualan harian, mingguan, bulanan)
  - Grafik penjualan
  - Peringatan stok rendah
  - Aturan asosiasi teratas
  - Laporan ringkasan

## Instalasi dan Konfigurasi

### Persyaratan Sistem
- Python 3.8 atau lebih tinggi
- pip (Python package installer)
- Git

### Langkah-langkah Instalasi

1. **Clone repositori** (jika belum):
   ```bash
   git clone https://github.com/[user]/manajemen_inventory.git
   cd manajemen_inventory
   ```

2. **Buat virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # atau
   venv\Scripts\activate  # Windows
   ```

3. **Instal dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Buat file konfigurasi .env**:
   ```
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```
   
   Contoh file .env:
   ```
   DJANGO_SECRET_KEY=django-insecure-development-key-for-testing-only
   DEBUG=True
   ```

5. **Inisialisasi database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **(Opsional) Isi database dengan data dummy**:
   ```bash
   python populate_dummy_data.py
   ```

7. **Jalankan server pengembangan**:
   ```bash
   python manage.py runserver
   ```

   Aplikasi akan tersedia di http://127.0.0.1:8000/

## Konfigurasi Database

Aplikasi ini menggunakan SQLite secara default, namun dapat dikonfigurasi untuk menggunakan database lain seperti PostgreSQL atau MySQL. Untuk mengganti database, ubah konfigurasi di `inventori/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # atau database lain
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Penggunaan Aplikasi

### Login Awal (Jika menggunakan data dummy)

Setelah menjalankan `populate_dummy_data.py`, beberapa akun telah dibuat:
- **Admin**: username: `admin`, password: `admin123`
- **Manager**: username: `manager`, password: `manager123`
- **Cashier**: username: `cashier`, password: `cashier123`
- **Warehouse**: username: `warehouse`, password: `warehouse123`
- **Analyst**: username: `analyst`, password: `analyst123`

### Peran Pengguna

- **Admin**: Akses penuh ke seluruh fitur aplikasi
- **Manager**: Akses ke dashboard, penjualan, pembelian, dan inventori
- **Cashier**: Akses ke fitur penjualan dan POS
- **Warehouse**: Akses ke manajemen inventori dan stok
- **Analyst**: Akses ke fitur analisis dan data mining

### Fitur Berdasarkan Peran

#### Admin
- Kelola semua data (produk, kategori, supplier, customer)
- Kelola pengguna dan hak akses
- Akses ke semua dashboard dan laporan
- Kelola inventori dan kebijakan pengadaan
- Lihat hasil analisis data mining

#### Manager
- Akses ke dashboard dan KPI
- Kelola penjualan dan pembelian
- Akses ke manajemen inventori
- Lihat hasil analisis data mining

#### Cashier
- Proses penjualan (POS)
- Cetak faktur
- Lihat ringkasan penjualan

#### Warehouse
- Kelola inventori dan stok
- Melihat pergerakan stok
- Melihat peringatan stok rendah
- Kelola kebijakan pengadaan

#### Analyst
- Akses ke hasil analisis data mining
- Lihat aturan asosiasi produk
- Akses ke dashboard analitik

## Struktur Database

### Tabel Master
- `category`: Kategori produk
- `product`: Produk
- `supplier`: Supplier
- `customer`: Customer
- `warehouse`: Gudang
- `user`: Pengguna

### Tabel Transaksi
- `sale`: Transaksi penjualan
- `sale_item`: Item penjualan
- `purchase_order`: Pesanan pembelian
- `po_item`: Item pesanan pembelian
- `goods_receipt`: Penerimaan barang
- `stock`: Stok produk per gudang
- `stock_move`: Histori pergerakan stok
- `reorder_policy`: Kebijakan pengadaan

### Tabel Analisis
- `association_rule`: Aturan asosiasi produk dari data mining

## API dan Integrasi

Aplikasi menyediakan beberapa endpoint API untuk keperluan integrasi:

- `/api/top-products/`: Data produk terlaris (untuk grafik)
- `/api/top-rules/`: Data aturan asosiasi teratas (untuk grafik)

## Development dan Deployment

### Development

Untuk pengembangan, gunakan server development bawaan Django:
```bash
python manage.py runserver
```

### Production

Untuk deployment ke production, perhatikan hal berikut:
1. Ganti `DEBUG = False` di settings
2. Gunakan database production (PostgreSQL disarankan)
3. Konfigurasi static files dengan web server (nginx, Apache)
4. Gunakan WSGI server seperti Gunicorn

Contoh deployment dengan Gunicorn:
```bash
pip install gunicorn
gunicorn inventori.wsgi:application
```

## Struktur Direktori

```
inventori/
├── manage.py
├── requirements.txt
├── .env
├── db.sqlite3
├── populate_dummy_data.py
├── accounts/           # Aplikasi autentikasi
├── master/             # Aplikasi master data
├── inventory/          # Aplikasi manajemen inventori
├── sales/              # Aplikasi penjualan
├── purchases/          # Aplikasi pembelian
├── mining/             # Aplikasi data mining
├── summary/            # Aplikasi dashboard
├── static/             # File statis
├── templates/          # Template HTML
└── inventori/          # Konfigurasi utama Django
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    └── asgi.py
```

## Data Dummy

File `populate_dummy_data.py` menyediakan data awal untuk pengujian dan demonstrasi aplikasi. Data yang dibuat meliputi:
- 5 pengguna dengan peran berbeda
- 5 kategori produk
- 12 produk
- 5 supplier
- 5 customer
- 3 gudang
- Stok awal untuk tiap produk di tiap gudang
- 5 pesanan pembelian
- 10 transaksi penjualan
- Aturan asosiasi produk

Eksekusi:
```bash
python populate_dummy_data.py
```

## Teknologi yang Digunakan

- **Backend**: Django (Python Web Framework)
- **Database**: SQLite (dapat dikonfigurasi ke PostgreSQL/MySQL)
- **Template**: Django Template Language
- **Autentikasi**: Django Auth System
- **Data Mining**: Algoritma Apriori (implementasi manual)
- **Environment**: python-decouple untuk konfigurasi
- **Form Styling**: crispy-forms dengan Bootstrap 5

## Lisensi

Dokumentasi ini disediakan sebagai bagian dari proyek aplikasi manajemen inventori.