-- ============================================================
-- TAHAP 2: REFACTORING SKEMA BINTANG & SCD TIPE 2
-- ============================================================

-- 1. Tabel Dimensi Pelanggan (SCD Tipe 2)
CREATE TABLE IF NOT EXISTS Dim_Customer (
    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    customer_name VARCHAR(100),
    city VARCHAR(50),
    membership_tier VARCHAR(20),
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT 1
);

-- 2. Tabel Dimensi Produk
CREATE TABLE IF NOT EXISTS Dim_Product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(100),
    unit_price DECIMAL(12,2)
);

-- 3. Tabel Dimensi Waktu
CREATE TABLE IF NOT EXISTS Dim_Date (
    date_key DATE PRIMARY KEY,
    day INTEGER,
    month INTEGER,
    year INTEGER,
    quarter INTEGER
);

-- 4. Tabel Fakta Transaksi (Skema Bintang)
CREATE TABLE IF NOT EXISTS Fact_Sales (
    sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,
    transaction_date DATE NOT NULL,
    customer_key INTEGER REFERENCES Dim_Customer(customer_key),
    product_id INTEGER REFERENCES Dim_Product(product_id),
    quantity INTEGER,
    total_amount DECIMAL(12,2)
);

-- ============================================================
-- TAHAP 3: OPTIMASI OLAP (PARTITIONING & MATERIALIZED VIEW / VIEW)
-- ============================================================

-- Indexing pada kolom tanggal transaksi untuk accelerasi filtering
CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON Fact_Sales(transaction_date);

-- View Agregasi Laporan Penjualan Harian (Akselerasi Query OLAP)
CREATE VIEW IF NOT EXISTS view_daily_sales_summary AS
SELECT 
    transaction_date,
    COUNT(sales_id) AS total_transactions,
    SUM(quantity) AS total_items_sold,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_basket_size
FROM Fact_Sales
GROUP BY transaction_date;
