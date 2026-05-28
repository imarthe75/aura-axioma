import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:casmarts_secure_db_pwd_2026@casmarts-core-db-primary:5432/db_core_knowledge")

DIVISIONS = {
    "10000000": "Materiales de consumo y materias primas (fauna, semillas, flora)",
    "11000000": "Materiales de minerales, tejidos y de plantas y animales no comestibles",
    "12000000": "Productos químicos, bioquímicos y gases industriales",
    "13000000": "Resina, colofonia, caucho, espuma, película y elastómeros",
    "14000000": "Materiales y productos de papel",
    "15000000": "Combustibles, aditivos, lubricantes y anticorrosivos",
    "20000000": "Maquinaria de minería, perforación y accesorios",
    "21000000": "Maquinaria y accesorios para agricultura, pesca, silvicultura y fauna",
    "22000000": "Maquinaria y accesorios para construcción y edificación",
    "23000000": "Maquinaria y accesorios para manufactura y procesamiento industrial",
    "24000000": "Maquinaria para manejo, acondicionamiento y almacenamiento de materiales",
    "25000000": "Vehículos comerciales, militares y privados, accesorios y componentes",
    "26000000": "Maquinaria y accesorios para generación y distribución de energía",
    "27000000": "Herramientas y maquinaria general",
    "30000000": "Componentes y suministros estructurales de construcción",
    "31000000": "Componentes y suministros para manufactura",
    "32000000": "Componentes, equipos y suministros electrónicos",
    "39000000": "Suministros de oficina, de consumo y de uso doméstico",
    "40000000": "Sistemas y componentes de distribución y acondicionamiento",
    "41000000": "Equipo de laboratorio, de medida, de observación y pruebas",
    "42000000": "Equipo, accesorios y suministros médicos",
    "43000000": "Tecnología de la información, telecomunicaciones y entretenimiento",
    "44000000": "Equipos, accesorios y suministros de oficina",
    "45000000": "Equipos y suministros de limpieza y de preparación de alimentos",
    "46000000": "Equipos de defensa, seguridad y protección",
    "47000000": "Equipos de consumo y suministros para el hogar",
    "48000000": "Maquinaria, equipos e instrumentos de servicio",
    "49000000": "Equipos, accesorios y suministros de recreación y deportes",
    "50000000": "Alimentos, bebidas y tabaco",
    "51000000": "Medicamentos y productos farmacéuticos",
    "52000000": "Artículos de consumo doméstico y personal",
    "53000000": "Ropa, calzado y equipamiento personal",
    "54000000": "Relojes, joyería y gemas",
    "55000000": "Publicaciones y material impreso",
    "56000000": "Muebles y mobiliario",
    "60000000": "Instrumentos musicales, juguetes, artesanías y suministros artísticos",
    "70000000": "Servicios de agricultura, silvicultura, pesca y fauna",
    "71000000": "Servicios de minería, petróleo y gas",
    "72000000": "Servicios de construcción y mantenimiento de edificios",
    "73000000": "Servicios de producción industrial y manufactura",
    "76000000": "Servicios de limpieza, saneamiento y eliminación de residuos",
    "77000000": "Servicios de medio ambiente",
    "78000000": "Servicios de transporte, almacenaje y correo",
    "80000000": "Servicios de gestión, consultoría y asistencia empresarial",
    "81000000": "Servicios informáticos, de TI y de telecomunicaciones",
    "82000000": "Servicios de publicidad, relaciones públicas y mercadotecnia",
    "83000000": "Servicios de utilidad pública",
    "84000000": "Servicios profesionales, científicos y técnicos",
    "85000000": "Servicios financieros, de seguros y de bienes raíces",
    "86000000": "Servicios de educación y capacitación",
    "90000000": "Servicios de salud, recreación, deportes y entretenimiento",
    "91000000": "Servicios personales, domésticos y sociales",
    "92000000": "Servicios de gobierno y defensa",
    "93000000": "Servicios políticos y de organizaciones no gubernamentales",
    "94000000": "Servicios de organizaciones religiosas y sociales",
    "95000000": "Terrenos, edificios y estructuras"
}

def clean_group_name(name):
    # Simplificaciones y limpieza para descripciones de grupos derivadas
    if not name:
        return ""
    name = name.strip()
    
    # Capitalizar la primera letra
    if len(name) > 0:
        name = name[0].upper() + name[1:]
    return name

def run():
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        # 1. Asegurar todas las Divisiones oficiales
        print("Ensuring official Divisions are populated...")
        for div_code, div_desc in DIVISIONS.items():
            # Check if division exists
            check = conn.execute(
                text("SELECT 1 FROM fiscal.cat_prod_serv WHERE code = :code AND scd_is_current = TRUE"),
                {"code": div_code}
            ).scalar()
            
            if not check:
                print(f"Adding missing division: {div_code} - {div_desc}")
                conn.execute(
                    text("""
                        INSERT INTO fiscal.cat_prod_serv (
                            code, description, active, scd_is_current, scd_version, scd_checksum, created_at, updated_at
                        ) VALUES (
                            :code, :desc, TRUE, TRUE, 1, md5(:code || '|' || :desc), NOW(), NOW()
                        )
                    """),
                    {"code": div_code, "desc": div_desc}
                )
        
        # 2. Encontrar todos los grupos de 4 dígitos activos basados en productos existentes
        print("Analyzing active group codes (4 digits) in the catalog...")
        res = conn.execute(text("""
            SELECT DISTINCT SUBSTRING(code, 1, 4) as group_prefix
            FROM fiscal.cat_prod_serv
            WHERE scd_is_current = TRUE AND length(code) = 8
        """))
        
        active_group_prefixes = [row[0] for row in res if row[0] and not row[0].endswith("00")]
        print(f"Found {len(active_group_prefixes)} active group prefixes. Checking database...")
        
        inserted_count = 0
        for prefix in active_group_prefixes:
            group_code = prefix + "0000"
            
            # Check if group exists
            check = conn.execute(
                text("SELECT 1 FROM fiscal.cat_prod_serv WHERE code = :code AND scd_is_current = TRUE"),
                {"code": group_code}
            ).scalar()
            
            if not check:
                # Find classes or products under this group prefix to derive description
                desc_row = conn.execute(
                    text("""
                        SELECT description 
                        FROM fiscal.cat_prod_serv 
                        WHERE code LIKE :class_pattern
                          AND code != :group_code
                          AND scd_is_current = TRUE
                        ORDER BY code
                        LIMIT 1
                    """),
                    {"class_pattern": prefix + "__00", "group_code": group_code}
                ).first()
                
                # If no classes, search for products under this prefix
                if not desc_row:
                    desc_row = conn.execute(
                        text("""
                            SELECT description 
                            FROM fiscal.cat_prod_serv 
                            WHERE code LIKE :prod_pattern
                              AND scd_is_current = TRUE
                            ORDER BY code
                            LIMIT 1
                        """),
                        {"prod_pattern": prefix + "____"}
                    ).first()
                
                derived_desc = "Grupo " + prefix
                if desc_row and desc_row[0]:
                    derived_desc = clean_group_name(desc_row[0])
                
                print(f"Adding missing group: {group_code} - {derived_desc}")
                conn.execute(
                    text("""
                        INSERT INTO fiscal.cat_prod_serv (
                            code, description, active, scd_is_current, scd_version, scd_checksum, created_at, updated_at
                        ) VALUES (
                            :code, :desc, TRUE, TRUE, 1, md5(:code || '|' || :desc), NOW(), NOW()
                        )
                    """),
                    {"code": group_code, "desc": derived_desc}
                )
                inserted_count += 1
                
        print(f"Successfully generated and inserted {inserted_count} missing groups.")
        print("SAT hierarchical references successfully populated!")

if __name__ == "__main__":
    run()
