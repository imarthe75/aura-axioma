import json
import psycopg2

# Conectar a la DB
conn = psycopg2.connect(
    host="localhost",
    port=5434,
    database="db_core_knowledge",
    user="admin",
    password="casmarts_secure_db_pwd_2026"
)
cur = conn.cursor()

# Leer JSON descargado completo
with open("/home/ia/ecosistema-casmarts/aura-axioma/api/scratch/countries_clean.json", "r", encoding="utf-8") as f:
    countries_data = json.load(f)

# Mapeo manual rápido para las principales nacionalidades en español
special_es = {
    "MEX": "Mexicana",
    "USA": "Estadounidense",
    "CAN": "Canadiense",
    "ESP": "Española",
    "FRA": "Francesa",
    "GBR": "Británica",
    "DEU": "Alemana",
    "ITA": "Italiana",
    "JPN": "Japonesa",
    "CHN": "China",
    "BRA": "Brasileña",
    "ARG": "Argentina",
    "COL": "Colombiana",
    "CHL": "Chilena",
    "PER": "Peruana",
    "VEN": "Venezolana",
    "CUB": "Cubana"
}

count = 0
for c in countries_data:
    cca3 = c.get("cca3")
    if not cca3:
        continue
    
    # Demonyms
    demonyms = c.get("demonyms", {})
    eng_dem = demonyms.get("eng", {}).get("m", "")
    fra_dem = demonyms.get("fra", {}).get("m", "")
    
    # Nacionalidad en español
    nat_es = special_es.get(cca3)
    if not nat_es and eng_dem:
        # Fallbacks estructurados
        if eng_dem.endswith("ian"):
            nat_es = eng_dem[:-3] + "ana"
        elif eng_dem.endswith("ese"):
            nat_es = eng_dem[:-3] + "esa"
        elif eng_dem.endswith("ish"):
            nat_es = eng_dem[:-3] + "esa"
        elif eng_dem.endswith("er"):
            nat_es = eng_dem[:-2] + "esa"
        else:
            nat_es = eng_dem + "a"
    
    # Si sigue vacío
    if not nat_es:
        nat_es = c.get("translations", {}).get("spa", {}).get("common", "")
        
    # Nacionalidad nativa
    nat_native = nat_es
    native_names = c.get("name", {}).get("native", {})
    if native_names:
        first_lang = list(native_names.keys())[0]
        nat_native = native_names[first_lang].get("common", nat_es)
        
    cur.execute("""
        UPDATE geo.paises 
        SET nationality_es = %s,
            nationality_en = %s,
            nationality_fr = %s,
            nationality_native = %s
        WHERE iso_alpha3 = %s AND scd_is_current = TRUE
    """, (nat_es, eng_dem, fra_dem, nat_native, cca3))
    count += cur.rowcount

conn.commit()
cur.close()
conn.close()
print(f"Se actualizaron {count} países con sus nacionalidades correctamente.")
BaseContent = "Actualización exitosa de base de datos."
