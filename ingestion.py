import json
import pandas as pd
from sqlalchemy import create_engine

# Koneksi ke Database SQLite (Lokal)
engine = create_engine('sqlite:///data_warehouse.db')

def run_ingestion():
    print("=== TAHAP 1: INGESTION PIPELINE ===")
    
    # 1. Ingest Data CSV
    df_csv = pd.read_csv('raw_sales.csv')
    df_csv.to_sql('stg_sales_csv', engine, if_exists='replace', index=False)
    print("✓ Data CSV berhasil dimuat ke tabel staging 'stg_sales_csv' (Rows:", len(df_csv), ")")
    
    # 2. Ingest Data JSON & Flattening
    with open('raw_logs.json') as f:
        logs_data = json.load(f)
    
    df_json = pd.json_normalize(logs_data)
    df_json.to_sql('stg_logs_json', engine, if_exists='replace', index=False)
    print("✓ Data JSON semi-terstruktur berhasil di-flatten & dimuat ke 'stg_logs_json' (Rows:", len(df_json), ")")

if __name__ == '__main__':
    run_ingestion()
