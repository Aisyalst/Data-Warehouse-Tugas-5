-- ============================================================
-- TAHAP 2 & 3: SKEMA BINTANG & OPTIMASI (VERSI MYSQL)
-- Proyek Kelompok: Riandi, Brian, Nicholas Capriconelius, Aisyal
-- ============================================================

-- Buat dan gunakan database
CREATE DATABASE IF NOT EXISTS data_warehouse_db;
USE data_warehouse_db;

-- 1. Tabel Dimensi Pelanggan (SCD Tipe 2)
CREATE TABLE IF NOT EXISTS Dim_Customer (
    customer_key INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    customer_name VARCHAR(100),
    city VARCHAR(50),
    membership_tier VARCHAR(20),
    start_date DATE NOT NULL,
    end_date DATE NULL,
    is_current BOOLEAN DEFAULT TRUE
);

-- 2. Tabel Dimensi Produk
CREATE TABLE IF NOT EXISTS Dim_Product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    unit_price DECIMAL(12,2)
);

-- 3. Tabel Dimensi Waktu
CREATE TABLE IF NOT EXISTS Dim_Date (
    date_key DATE PRIMARY KEY,
    day INT,
    month INT,
    year INT,
    quarter INT
);

-- 4. Tabel Fakta Transaksi (Skema Bintang + Partitioning by Range Date)
CREATE TABLE IF NOT EXISTS Fact_Sales (
    sales_id INT AUTO_INCREMENT,
    transaction_id INT,
    transaction_date DATE NOT NULL,
    customer_key INT,
    product_id INT,
    quantity INT,
    total_amount DECIMAL(12,2),
    PRIMARY KEY (sales_id, transaction_date),
    FOREIGN KEY (customer_key) REFERENCES Dim_Customer(customer_key),
    FOREIGN KEY (product_id) REFERENCES Dim_Product(product_id)
)
PARTITION BY RANGE (YEAR(transaction_date)) (
    PARTITION p_2025 VALUES LESS THAN (2026),
    PARTITION p_2026 VALUES LESS THAN (2027),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- ============================================================
-- OPTIMASI OLAP: MATERIALIZED VIEW SIMULATION (MENGGUNAKAN VIEW / EVENT)
-- ============================================================

-- Indexing untuk mempercepat filter pencarian
CREATE INDEX idx_fact_sales_date ON Fact_Sales(transaction_date);

-- Membuat View Agregasi Laporan Harian (Akselerasi Query OLAP)
CREATE OR REPLACE VIEW view_daily_sales_summary AS
SELECT 
    transaction_date,
    COUNT(sales_id) AS total_transactions,
    SUM(quantity) AS total_items_sold,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_basket_size
FROM Fact_Sales
GROUP BY transaction_date;
