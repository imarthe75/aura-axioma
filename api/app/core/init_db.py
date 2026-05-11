import os
from sqlalchemy import create_engine, text
from app.core.config import settings

def init_db():
    engine = create_engine(settings.DATABASE_URL)
    
    # Path to init scripts
    init_path = "/app/database/init"
    if not os.path.exists(init_path):
        # Local path if running outside docker for dev
        init_path = "database/init"
        
    scripts = sorted([f for f in os.listdir(init_path) if f.endswith(".sql")])
    
    # Also add the scd2_utils script
    scripts_path = "/app/database/scripts"
    if not os.path.exists(scripts_path):
        scripts_path = "database/scripts"
    
    with engine.begin() as conn:
        print(f"Running database initialization on {settings.DATABASE_URL}...")
        
        # 1. Run init scripts
        for script in scripts:
            print(f"Executing {script}...")
            with open(os.path.join(init_path, script), "r") as f:
                sql = f.read()
                conn.execute(text(sql))
        
        # 2. Run utils
        print("Executing 02_scd2_utils.sql...")
        with open(os.path.join(scripts_path, "02_scd2_utils.sql"), "r") as f:
            sql = f.read()
            conn.execute(text(sql))
            
    print("Database initialization completed.")

if __name__ == "__main__":
    init_db()
