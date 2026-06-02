import os
from sqlalchemy import create_engine, text

db_url = os.environ.get("DATABASE_URL", "postgresql://admin:casmarts_secure_db_pwd_2026@10.4.3.10:5432/db_core_knowledge")
# Wait, let's use the local port if 10.4.3.10 is the core DB or if we can run it via docker.
# Let's inspect docker network or resolve host casmarts-core-db-primary or 10.4.3.10.
# In docker-compose, casmarts-core-db-primary is on aura-network.
# Let's see if we can connect to postgresql://admin:casmarts_secure_db_pwd_2026@10.4.3.10:5432/db_core_knowledge
engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        print("Connected to DB successfully!")
        
        # 1. Check countries count and list
        res_countries = conn.execute(text("SELECT id, iso_alpha3, name, scd_is_current FROM geo.paises ORDER BY name;"))
        countries = [dict(row._asdict()) for row in res_countries]
        print(f"Total countries in geo.paises: {len(countries)}")
        print("First 10 countries:")
        for c in countries[:10]:
            print(c)
            
        # 2. Check if inegi schema exists and localidades count
        res_localidades = conn.execute(text("SELECT COUNT(*) FROM inegi.localidades;"))
        count_loc = res_localidades.scalar()
        print(f"Total localities in inegi.localidades: {count_loc}")
        
except Exception as e:
    print(f"Error connecting to DB: {e}")
