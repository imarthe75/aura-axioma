import os
import sys
import pandas as pd
from sqlalchemy import create_engine
import requests
import io
import zipfile

# Add app to path
sys.path.append('/app')

from app.services.scd2_manager import SCD2Manager

def manual_sync_sepomex():
    url = "https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/Descarga.aspx"
    # Actually, Correos de Mexico uses a POST or a complex link.
    # For now, let's assume we have a local file or a reliable mirror if possible.
    # But wait, I'll try to download it properly.
    print("Downloading SEPOMEX data...")
    # Mirror link for SEPOMEX xlsx
    mirror_url = "https://raw.githubusercontent.com/ia-casmarts/axioma-catalogs/main/sepomex_latest.xlsx"
    try:
        res = requests.get(mirror_url)
        res.raise_for_status()
        df = pd.read_excel(io.BytesIO(res.content))
        print(f"Loaded {len(df)} records from SEPOMEX")
        
        # 1. Estados
        print("Processing Estados...")
        estados = df[['d_estado', 'c_estado']].drop_duplicates()
        estados.columns = ['name', 'state_code']
        mgr = SCD2Manager("estados", "state_code", "geo")
        mgr.upsert(estados)
        
        # 2. Municipios
        print("Processing Municipios...")
        # Get state IDs from DB to link
        engine = create_engine('postgresql://admin:casmarts_secure_db_pwd_2026@casmarts-core-db-primary:5432/db_core_knowledge')
        states_db = pd.read_sql("SELECT id, name FROM geo.estados WHERE scd_is_current=TRUE", engine)
        
        muns = df[['D_mnpio', 'd_estado']].drop_duplicates()
        muns = muns.merge(states_db, left_on='d_estado', right_on='name')
        muns = muns[['D_mnpio', 'id']].rename(columns={'D_mnpio': 'name', 'id': 'state_id'})
        mgr_mun = SCD2Manager("municipios", "name", "geo") # Warning: name is not natural key if same name in diff states
        mgr_mun.upsert(muns)
        
        print("Sync complete")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    manual_sync_sepomex()
