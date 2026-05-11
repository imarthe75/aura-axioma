import pandas as pd
from sqlalchemy import create_engine, text
from app.core.config import settings
import hashlib
import json

class SCD2Manager:
    def __init__(self, target_table: str, natural_key: str, schema: str):
        self.target_table = target_table
        self.natural_key = natural_key
        self.schema = schema
        self.engine = create_engine(settings.DATABASE_URL)

    def _calculate_checksum(self, df: pd.DataFrame, exclude_cols: list) -> pd.Series:
        # Sort columns to ensure consistent hashing
        cols = sorted([c for c in df.columns if c not in exclude_cols])
        return df[cols].apply(lambda x: hashlib.md5(x.to_json().encode()).hexdigest(), axis=1)

    def process_dataframe(self, df: pd.DataFrame):
        staging_table = f"staging_{self.target_table}"
        
        # 1. Prepare data (clean strings, handle nulls)
        df = df.fillna("")
        
        # 2. Calculate checksum for staging data
        exclude_from_hash = [self.natural_key, 'scd_start_date', 'scd_end_date', 'scd_is_current', 'scd_version', 'scd_checksum']
        df['scd_checksum'] = self._calculate_checksum(df, exclude_from_hash)
        
        # 3. Load to staging schema
        df.to_sql(staging_table, self.engine, schema='staging', if_exists='replace', index=False)
        
        # 4. Execute SCD2 Merge Logic
        with self.engine.begin() as conn:
            # A. Close modified records
            close_query = text(f"""
                UPDATE {self.schema}.{self.target_table} t
                SET scd_is_current = FALSE,
                    scd_end_date = NOW(),
                    updated_at = NOW()
                FROM staging.{staging_table} s
                WHERE t.{self.natural_key}::text = s.{self.natural_key}::text
                  AND t.scd_is_current = TRUE
                  AND t.scd_checksum != s.scd_checksum;
            """)
            conn.execute(close_query)
            
            # B. Insert new records or new versions
            insert_query = text(f"""
                INSERT INTO {self.schema}.{self.target_table} (
                    {", ".join(df.columns)}, 
                    scd_start_date, scd_end_date, scd_is_current, scd_version, created_at, updated_at
                )
                SELECT 
                    s.*, 
                    NOW(), '9999-12-31', TRUE,
                    COALESCE((SELECT MAX(scd_version) FROM {self.schema}.{self.target_table} WHERE {self.natural_key}::text = s.{self.natural_key}::text), 0) + 1,
                    NOW(), NOW()
                FROM staging.{staging_table} s
                WHERE NOT EXISTS (
                    SELECT 1 FROM {self.schema}.{self.target_table} t 
                    WHERE t.{self.natural_key}::text = s.{self.natural_key}::text 
                      AND t.scd_is_current = TRUE
                );
            """)
            conn.execute(insert_query)
            
        return {"status": "success", "processed_records": len(df)}

    def upsert(self, df: pd.DataFrame):
        return self.process_dataframe(df)

    def search(self, search_term: str = None, limit: int = 10, **filters):
        """Basic keyword search on current records"""
        with self.engine.connect() as conn:
            where_clauses = ["scd_is_current = TRUE"]
            params = {}
            
            if search_term:
                # Search on natural key and common text fields
                search_fields = [f"{self.natural_key}::text", "name", "nombre", "description", "descripcion"]
                # We filter only existing columns in a real scenario, but for now we'll use COALESCE/OR
                search_conds = " OR ".join([f"{f} ILIKE :term" for f in search_fields])
                where_clauses.append(f"({search_conds})")
                params["term"] = f"%{search_term}%"
            
            for key, value in filters.items():
                where_clauses.append(f"{key} = :{key}")
                params[key] = value
                
            where_sql = " AND ".join(where_clauses)
            sql = f"SELECT * FROM {self.schema}.{self.target_table} WHERE {where_sql} LIMIT {limit}"
            
            result = conn.execute(text(sql), params)
            return [dict(row._asdict()) for row in result]
