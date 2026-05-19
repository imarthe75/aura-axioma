from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.begin() as conn:
    try:
        # Try a simple cast
        res = conn.exec_driver_sql('SELECT "municipality_id"::uuid FROM staging.staging_asentamientos LIMIT 1')
        print(f"Success 1: {res.fetchone()}")
        
        res = conn.exec_driver_sql('SELECT CAST("municipality_id" AS uuid) FROM staging.staging_asentamientos LIMIT 1')
        print(f"Success 2: {res.fetchone()}")
        
        res = conn.exec_driver_sql('SELECT src."municipality_id"::uuid FROM staging.staging_asentamientos src LIMIT 1')
        print(f"Success 3: {res.fetchone()}")

    except Exception as e:
        print(f"Error: {e}")
