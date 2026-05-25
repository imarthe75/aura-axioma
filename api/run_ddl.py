import os
from sqlalchemy import create_engine, text

def main():
    db_url = os.getenv("DATABASE_URL", "postgresql://admin:casmarts_secure_db_pwd_2026@casmarts-core-db-primary:5432/db_core_knowledge")
    print(f"Connecting to database...")
    engine = create_engine(db_url)
    
    sql_file = "/app/database/init/09_refactor_axioma_ddl.sql"
    print(f"Reading SQL file: {sql_file}")
    with open(sql_file, "r") as f:
        sql_content = f.read()
        
    # Split by semicolon to execute statement by statement to avoid transaction issues with extensions
    # but be careful with functions/triggers. Our DDL has plain statements, so splitting by semicolon is fine.
    # Actually, we can also execute the whole block if PostgreSQL allows it.
    with engine.begin() as conn:
        print("Executing DDL statements...")
        # To avoid issues with CREATE EXTENSION, let's execute the raw script or split it.
        # PostgreSQL supports running multi-statement query blocks in connection.execute(text(...))
        conn.execute(text(sql_content))
        print("DDL Refactoring applied successfully!")

if __name__ == "__main__":
    main()
