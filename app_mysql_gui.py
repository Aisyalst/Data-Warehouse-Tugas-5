import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt
from sqlalchemy import create_engine, text

# Koneksi ke database MySQL local
DB_URI = 'mysql+pymysql://root:@localhost:3306/data_warehouse_db'

class MySQLWarehouseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Analitik Penjualan - Tugas Kelompok")
        self.setGeometry(100, 100, 1000, 580)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Judul Utama dengan Warna yang Cerah, Menarik, dan Mudah Dipahami
        title_label = QLabel("LAPORAN HARIAN PENJUALAN")
        title_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #000000; 
            background-color: #E0E0E0; 
            padding: 8px; 
            qproperty-alignment: 'AlignCenter';
            margin-bottom: 5px;
        """)
        main_layout.addWidget(title_label)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Tab 1: Ringkasan OLAP View
        self.tab_olap = QWidget()
        self.init_table_tab(self.tab_olap, "view_daily_sales_summary")
        self.tabs.addTab(self.tab_olap, "📈 Laporan Ringkasan Harian (OLAP)")
        
        # Tab 2: Tabel Fakta Sales
        self.tab_fact = QWidget()
        self.init_table_tab(self.tab_fact, "fact_sales")
        self.tabs.addTab(self.tab_fact, "⭐ Tabel Fakta Penjualan Utama")
        
        # Tab 3: Staging CSV
        self.tab_stg = QWidget()
        self.init_table_tab(self.tab_stg, "stg_sales_csv")
        self.tabs.addTab(self.tab_stg, "📂 Data Mentah Staging CSV")
        
        # Tombol Aksi
        btn_layout = QHBoxLayout()
        self.btn_process = QPushButton("🚀 Proses ETL & Sinkronisasi Data")
        self.btn_process.setStyleSheet("background-color: #0288D1; color: white; font-weight: bold; padding: 10px; font-size: 13px; border-radius: 4px;")
        self.btn_process.clicked.connect(self.run_etl_transformation)
        btn_layout.addWidget(self.btn_process)
        
        self.btn_refresh = QPushButton("🔄 Segarkan Tampilan Data")
        self.btn_refresh.setStyleSheet("background-color: #388E3C; color: white; font-weight: bold; padding: 10px; font-size: 13px; border-radius: 4px;")
        self.btn_refresh.clicked.connect(self.load_all_data)
        btn_layout.addWidget(self.btn_refresh)
        
        main_layout.addLayout(btn_layout)
        self.load_all_data()

    def init_table_tab(self, tab_widget, table_name):
        layout = QVBoxLayout(tab_widget)
        table = QTableWidget()
        layout.addWidget(table)
        setattr(tab_widget, 'table_view', table)
        setattr(tab_widget, 'target_table', table_name)

    def run_etl_transformation(self):
        try:
            engine = create_engine(DB_URI)
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT IGNORE INTO Dim_Customer (customer_id, customer_name, city, membership_tier, start_date, is_current)
                    SELECT DISTINCT customer_id, customer_name, city, membership_tier, '2025-01-01', 1 FROM stg_sales_csv;
                """))
                conn.execute(text("""
                    INSERT IGNORE INTO Dim_Product (product_id, product_name, unit_price)
                    SELECT DISTINCT product_id, product_name, price FROM stg_sales_csv;
                """))
                res = conn.execute(text("SELECT COUNT(*) FROM fact_sales")).scalar()
                if res == 0:
                    conn.execute(text("""
                        INSERT INTO Fact_Sales (transaction_id, transaction_date, customer_key, product_id, quantity, total_amount)
                        SELECT 
                            s.transaction_id, 
                            STR_TO_DATE(s.transaction_date, '%Y-%m-%d'), 
                            c.customer_key, 
                            s.product_id, 
                            s.quantity, 
                            (s.quantity * s.price)
                        FROM stg_sales_csv s
                        JOIN Dim_Customer c ON s.customer_id = c.customer_id AND c.is_current = 1;
                    """))
            QMessageBox.information(self, "Berhasil", "Proses ETL dan Sinkronisasi data berhasil dijalankan!")
            self.load_all_data()
        except Exception as e:
            QMessageBox.critical(self, "Terjadi Kesalahan", f"Pesan Error:\n{str(e)}")

    def load_all_data(self):
        try:
            engine = create_engine(DB_URI)
            for tab in [self.tab_olap, self.tab_fact, self.tab_stg]:
                table_name = getattr(tab, 'target_table')
                table_widget = getattr(tab, 'table_view')
                df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
                
                # Mengubah nama kolom agar menggunakan bahasa Indonesia yang rapi
                rename_map = {
                    'transaction_id': 'ID Transaksi',
                    'customer_id': 'ID Pelanggan',
                    'customer_name': 'Nama Pelanggan',
                    'city': 'Kota',
                    'membership_tier': 'Tingkat Member',
                    'product_id': 'ID Produk',
                    'product_name': 'Nama Produk',
                    'quantity': 'Jumlah',
                    'price': 'Harga Satuan',
                    'transaction_date': 'Tanggal Transaksi',
                    'sales_id': 'ID Penjualan',
                    'customer_key': 'Kunci Pelanggan',
                    'total_amount': 'Total Harga',
                    'total_transactions': 'Total Transaksi',
                    'total_items_sold': 'Total Barang Terjual',
                    'total_revenue': 'Total Pendapatan',
                    'avg_basket_size': 'Rata-rata Ukuran Keranjang'
                }
                df = df.rename(columns=rename_map)
                self.populate_table(table_widget, df)
        except Exception as e:
            QMessageBox.critical(self, "Koneksi Gagal", f"Tidak dapat terhubung ke database:\n{str(e)}")

    def populate_table(self, table_widget, df):
        table_widget.setRowCount(len(df))
        table_widget.setColumnCount(len(df.columns))
        table_widget.setHorizontalHeaderLabels(df.columns.astype(str))
        
        for i in range(len(df)):
            for j in range(len(df.columns)):
                val = df.iloc[i, j]
                col_name = df.columns[j].lower()
                
                # Format angka dan harga agar menggunakan pemisah titik (ribuan)
                if isinstance(val, (int, float)) and ('harga' in col_name or 'pendapatan' in col_name or 'total' in col_name or 'rata' in col_name):
                    text_val = f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                else:
                    text_val = str(val)
                    
                item = QTableWidgetItem(text_val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table_widget.setItem(i, j, item)
        table_widget.resizeColumnsToContents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MySQLWarehouseApp()
    window.show()
    sys.exit(app.exec())