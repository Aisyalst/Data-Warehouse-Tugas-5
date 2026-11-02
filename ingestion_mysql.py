import json
import pandas as pd
from sqlalchemy import create_engine

# Koneksi ke Database MySQL (Ganti 'root' dan 'password' sesuai XAMPP/MySQL lokal Anda)
# Format: mysql+pymysql://username:password@host:port/database_name
engine = create_engine('mysql+pymysql://root:@localhost:3306/data_warehouse_db')

def run_ingestion_mysql():
    print("=== TAHAP 1: INGESTION PIPELINE KE MYSQL ===")
    
    # 1. Ingest Data CSV
    df_csv = pd.read_csv('raw_sales.csv')
    df_csv.to_sql('stg_sales_csv', engine, if_exists='replace', index=False)
    print("✓ Data CSV berhasil dimuat ke tabel staging MySQL 'stg_sales_csv' (Rows:", len(df_csv), ")")
    
    # 2. Ingest Data JSON & Flattening
    with open('raw_logs.json') as f:
        logs_data = json.load(f)
    
    df_json = pd.json_normalize(logs_data)
    df_json.to_sql('stg_logs_json', engine, if_exists='replace', index=False)
    print("✓ Data JSON semi-terstruktur berhasil di-flatten & dimuat ke MySQL 'stg_logs_json' (Rows:", len(df_json), ")")

if __name__ == '__main__':
    run_ingestion_mysql()
