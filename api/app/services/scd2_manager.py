import pandas as pd
from sqlalchemy import create_engine, text
from app.core.config import settings
import hashlib
from typing import Union, List
import numpy as np

class SCD2Manager:
    def __init__(self, target_table: str, natural_key: Union[str, List[str]], schema: str):
        self.target_table = target_table
        self.natural_keys = [natural_key] if isinstance(natural_key, str) else natural_key
        self.schema = schema
        self.engine = create_engine(settings.DATABASE_URL)

    def _calculate_checksum(self, df: pd.DataFrame, exclude_cols: list) -> pd.Series:
        cols = sorted([c for c in df.columns if c not in exclude_cols])
        # Vectorized approach: join columns and hash the resulting strings
        # This is much faster and more memory-efficient than iterrows
        concat_series = df[cols].fillna("").astype(str).agg("".join, axis=1)
        return concat_series.apply(lambda x: hashlib.md5(x.encode('utf-8', errors='replace')).hexdigest())

    def process_dataframe(self, df: pd.DataFrame):
        staging_table = f"staging_{self.target_table}"
        
        # 1. Prepare data
        df = df.fillna("")
        
        # 2. Calculate checksum for staging data
        exclude_from_hash = self.natural_keys + ['scd_start_date', 'scd_end_date', 'scd_is_current', 'scd_version', 'scd_checksum']
        df['scd_checksum'] = self._calculate_checksum(df, exclude_from_hash)
        
        # 3. Load to staging schema
        print(f"Loading {len(df)} records to staging.{staging_table}...")
        df.to_sql(staging_table, self.engine, schema='staging', if_exists='replace', index=False, chunksize=10000)
        print(f"Loading complete.")
        
        # 4. Execute SCD2 Merge Logic
        with self.engine.begin() as conn:
            # Set search path to ensure schemas are visible
            conn.execute(text(f"SET search_path TO {self.schema}, staging, public"))
            
            # Build Join Condition
            staging_join = " AND ".join([f's."{nk}"::text = t."{nk}"::text' for nk in self.natural_keys])
            
            # Index staging table for performance
            idx_name = f"idx_staging_{self.target_table}_nk"
            nk_cols = ", ".join([f'"{nk}"' for nk in self.natural_keys])
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON staging.{staging_table} ({nk_cols})"))
            conn.execute(text(f"ANALYZE staging.{staging_table}"))
            
            # A. Close modified records
            close_query = f"""
                UPDATE {self.schema}.{self.target_table} t
                SET scd_is_current = FALSE,
                    scd_end_date = NOW(),
                    updated_at = NOW()
                FROM staging.{staging_table} src
                WHERE {" AND ".join([f'src."{nk}"::text = t."{nk}"::text' for nk in self.natural_keys])}
                  AND t.scd_is_current = TRUE
                  AND t.scd_checksum != src.scd_checksum;
            """
            conn.exec_driver_sql(close_query)
            
            # B. Insert new records or new versions (SCD2)
            target_cols_list = [c for c in df.columns if c != 'id']
            target_cols_str = ", ".join([f'"{c}"' for c in target_cols_list])
            cols = [c for c in df.columns if c not in ['id', 'scd_checksum']]
            cols.append('scd_checksum')
            
            # Build SELECT list with explicit UUID casting for foreign keys
            source_cols_list = []
            for c in cols:
                if c.endswith('_id'):
                    source_cols_list.append(f'NULLIF(src."{c}", \'\')::uuid')
                elif c == 'metadata':
                    source_cols_list.append(f'NULLIF(src."{c}", \'\')::jsonb')
                else:
                    source_cols_list.append(f'src."{c}"')
            source_cols = ", ".join(source_cols_list)
            
            target_cols = ", ".join([f'"{c}"' for c in cols])
            
            # Build join condition for the MAX version subquery
            join_cond = " AND ".join([f'v."{nk}"::text = src."{nk}"::text' for nk in self.natural_keys])
            # Build existence check condition
            exist_cond = " AND ".join([f't."{nk}"::text = src."{nk}"::text' for nk in self.natural_keys])
            # Build distinct on columns
            distinct_on = ", ".join([f'src."{nk}"' for nk in self.natural_keys])
            # Build order by columns (must match distinct on)
            order_by = ", ".join([f'src."{nk}"' for nk in self.natural_keys])

            insert_query = f"""
                INSERT INTO {self.schema}.{self.target_table} (
                    {target_cols}, scd_start_date, scd_end_date, scd_is_current, scd_version, created_at, updated_at
                )
                SELECT DISTINCT ON ({distinct_on})
                    {source_cols}, 
                    NOW(), '9999-12-31', TRUE,
                    COALESCE(
                        (SELECT MAX(scd_version) 
                         FROM {self.schema}.{self.target_table} v 
                         WHERE {join_cond}
                        ), 0
                    ) + 1,
                    NOW(), NOW()
                FROM staging.{staging_table} src
                WHERE NOT EXISTS (
                    SELECT 1 FROM {self.schema}.{self.target_table} t 
                    WHERE {exist_cond}
                      AND t.scd_is_current = TRUE
                )
                ORDER BY {order_by};
            """
            conn.execute(text(insert_query))
            
        return {"status": "success", "processed_records": len(df)}

    def upsert(self, df: pd.DataFrame):
        return self.process_dataframe(df)

    def search(self, search_term: str = None, limit: int = 10, **filters):
        """Basic keyword search on current records"""
        with self.engine.connect() as conn:
            where_clauses = ["scd_is_current = TRUE"]
            params = {}
            
            if search_term:
                # Search on natural keys and common text fields
                search_fields = [f"{nk}::text" for nk in self.natural_keys] + ["name", "nombre", "description", "descripcion"]
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
