import os
from sqlalchemy import create_engine, text

def main():
    db_url = os.getenv("DATABASE_URL", "postgresql://admin:casmarts_secure_db_pwd_2026@localhost:5434/db_core_knowledge")
    engine = create_engine(db_url)
    
    with engine.begin() as conn:
        print("Obteniendo municipios...")
        res = conn.execute(text("SELECT id, name FROM geo.municipios WHERE scd_is_current = TRUE"))
        municipalities = [dict(r._mapping) for r in res]
        print(f"Encontrados {len(municipalities)} municipios.")
        
        # Clear existing mock/old records
        conn.execute(text("DELETE FROM inegi.localidades"))
        print("Registros anteriores de inegi.localidades eliminados.")
        
        count = 0
        for m in municipalities:
            mun_id = m['id']
            mun_name = m['name']
            
            # Seed 2 localities for each municipality
            localities_data = [
                {
                    "clave": "0001",
                    "nombre": f"Cabecera Municipal de {mun_name}",
                    "lat": 19.4326 + (count * 0.001) % 0.5,
                    "lon": -99.1332 - (count * 0.001) % 0.5,
                    "alt": 2240 + (count % 200)
                },
                {
                    "clave": "0002",
                    "nombre": f"Colonia Linda Vista de {mun_name}",
                    "lat": 19.4346 + (count * 0.001) % 0.5,
                    "lon": -99.1312 - (count * 0.001) % 0.5,
                    "alt": 2250 + (count % 200)
                }
            ]
            
            for loc in localities_data:
                query = text("""
                    INSERT INTO inegi.localidades (
                        id, municipality_id, clave_localidad, nombre, latitud, longitud, altitud, 
                        scd_is_current, scd_version, scd_checksum, geom
                    ) VALUES (
                        gen_random_uuid(), :mun_id, :clave, :nombre, :lat, :lon, :alt, 
                        TRUE, 1, 'seeded_mock', ST_SetSRID(ST_Point(:lon, :lat), 4326)
                    )
                """)
                conn.execute(query, {
                    "mun_id": mun_id,
                    "clave": loc["clave"],
                    "nombre": loc["nombre"],
                    "lat": loc["lat"],
                    "lon": loc["lon"],
                    "alt": loc["alt"]
                })
            
            count += 1
            
        print(f"Se sembraron {count * 2} localidades exitosamente en inegi.localidades.")

if __name__ == "__main__":
    main()
