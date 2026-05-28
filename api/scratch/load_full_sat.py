import os
import json
import urllib.request
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@casmarts-core-db-primary:5432/db_core_knowledge")

def download_and_load():
    url = "https://raw.githubusercontent.com/bambucode/catalogos_sat_JSON/master/c_ClaveProdServ.json"
    print("Downloading full SAT product catalog...")
    
    try:
        # Download file
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error downloading catalog: {e}")
        return
        
    print(f"Downloaded {len(data)} records. Sample record keys: {list(data[0].keys()) if data else 'Empty'}. Processing...")
    
    records = []
    for item in data:
        # The key for code in this JSON is 'id'
        code = item.get("id") or item.get("c_ClaveProdServ") or item.get("c_claveprodserv")
        desc = item.get("descripcion") or item.get("description") or item.get("nombre")
        
        if not code or not desc:
            continue
            
        # Ensure code is string of length 8
        code = str(code).strip().zfill(8)
        if len(code) != 8:
            continue
            
        # Check active status based on fechaFinVigencia
        fin = item.get("fechaFinVigencia")
        # If active/inactive
        active = True
        if fin:
            active = False
            
        records.append({
            "code": code,
            "description": desc,
            "active": active
        })
        
    df = pd.DataFrame(records)
    print(f"Normalized {len(df)} records. Connecting to DB...")
    
    engine = create_engine(DATABASE_URL)
    
    # Let's perform batch inserts using staging or direct SQL to ensure super fast loading
    # To handle SCD2 or unique constraint:
    # Since we want a complete catalog, we can load it to a staging table or upsert directly.
    # Let's do a direct bulk upsert!
    print("Beginning bulk load into fiscal.cat_prod_serv...")
    
    # We will slice and upload in chunks
    chunk_size = 5000
    with engine.begin() as conn:
        # Create a temp table
        conn.execute(text("CREATE TEMP TABLE temp_sat (code VARCHAR(20), description TEXT, active BOOLEAN);"))
        
        # Load into temp table using pandas
        df.to_sql("temp_sat", conn, if_exists="append", index=False, method="multi", chunksize=1000)
        print("Data loaded to temp table. Performing SCD2 Upsert/Merge...")
        
        # Inserciones y actualizaciones
        # 1. Deactivar registros existentes que cambiaron de descripción o estado
        # 2. Insertar registros nuevos
        upsert_query = """
            -- Deactivate old versions if description changed
            UPDATE fiscal.cat_prod_serv t
            SET scd_is_current = FALSE, scd_end_date = NOW(), updated_at = NOW()
            FROM temp_sat s
            WHERE t.code = s.code 
              AND t.scd_is_current = TRUE 
              AND (t.description <> s.description OR t.active <> s.active);
              
            -- Insert new versions or totally new codes
            INSERT INTO fiscal.cat_prod_serv (
                code, description, scd_is_current, scd_version, scd_checksum, created_at, updated_at
            )
            SELECT 
                s.code, 
                s.description, 
                TRUE, 
                COALESCE((SELECT MAX(scd_version) + 1 FROM fiscal.cat_prod_serv WHERE code = s.code), 1),
                md5(s.code || '|' || s.description),
                NOW(),
                NOW()
            FROM temp_sat s
            WHERE NOT EXISTS (
                SELECT 1 FROM fiscal.cat_prod_serv t 
                WHERE t.code = s.code AND t.scd_is_current = TRUE
            );
        """
        conn.execute(text(upsert_query))
        print("SCD2 Upsert/Merge complete.")
        
    print("Catalog successfully fully populated!")

if __name__ == "__main__":
    download_and_load()
