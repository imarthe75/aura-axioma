import pandas as pd
from sqlalchemy import create_engine, text
from app.core.config import settings
import hashlib
from typing import Union, List

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
        concat_series = df[cols].astype(str).agg("".join, axis=1)
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
            join_cond = " AND ".join([f't."{nk}"::text = s."{nk}"::text' for nk in self.natural_keys])
            staging_join = " AND ".join([f's."{nk}"::text = t."{nk}"::text' for nk in self.natural_keys])
            
            # Index staging table for performance
            idx_name = f"idx_staging_{self.target_table}_nk"
            nk_cols = ", ".join([f'"{nk}"' for nk in self.natural_keys])
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON staging.{staging_table} ({nk_cols})"))
            conn.execute(text(f"ANALYZE staging.{staging_table}"))
            
            # A. Close modified records
            close_query = text(f"""
                UPDATE {self.target_table} t
                SET scd_is_current = FALSE,
                    scd_end_date = NOW(),
                    updated_at = NOW()
                FROM staging.{staging_table} s
                WHERE {staging_join}
                  AND t.scd_is_current = TRUE
                  AND t.scd_checksum != s.scd_checksum;
            """)
            conn.execute(close_query)
            
            # B. Insert new records or new versions
            target_cols_list = [c for c in df.columns if c != 'id']
            target_cols_str = ", ".join([f'"{c}"' for c in target_cols_list])
            
            # Source columns with appropriate casting
            source_cols_list = []
            for c in target_cols_list:
                if c.endswith('_id'):
                    source_cols_list.append(f'"{c}"::uuid')
                else:
                    source_cols_list.append(f'"{c}"')
            source_cols_str = ", ".join(source_cols_list)
            
            # Optimized Insert using a CTE to handle casting once
            insert_query = text(f"""
                WITH staged_data AS (
                    SELECT {", ".join([f'"{c}"' for c in target_cols_list])}
                    FROM staging.{staging_table}
                ),
                versions AS (
                    SELECT {nk_cols}, MAX(scd_version) as max_version 
                    FROM {self.target_table} 
                    GROUP BY {nk_cols}
                )
                INSERT INTO {self.target_table} (
                    {target_cols_str}, 
                    scd_start_date, scd_end_date, scd_is_current, scd_version, created_at, updated_at
                )
                SELECT 
                    {source_cols_str}, 
                    NOW(), '9999-12-31', TRUE,
                    COALESCE(v.max_version, 0) + 1,
                    NOW(), NOW()
                FROM staged_data s
                LEFT JOIN versions v ON {" AND ".join([f's."{nk}"::text = v."{nk}"::text' for nk in self.natural_keys])}
                WHERE NOT EXISTS (
                    SELECT 1 FROM {self.target_table} t 
                    WHERE {" AND ".join([f's."{nk}"::text = t."{nk}"::text' for nk in self.natural_keys])}
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
