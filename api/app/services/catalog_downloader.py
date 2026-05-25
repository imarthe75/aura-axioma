import holidays
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from datetime import date
import logging
from sqlalchemy import text
from app.services.scd2_manager import SCD2Manager
from app.core.celery_app import celery_app

class CatalogDownloader:
    @staticmethod
    @celery_app.task(name="app.services.catalog_downloader.sync_all_catalogs")
    def sync_all_catalogs():
        """Master task to sync everything"""
        CatalogDownloader.sync_holidays()
        CatalogDownloader.sync_sepomex_local()
        CatalogDownloader.sync_casfim()
        CatalogDownloader.sync_sat_catalogs()
        return {"status": "all_sync_triggered"}

    @staticmethod
    def sync_sat_catalogs():
        """Sync Anexo 20 Catalogs for Invoicing (SAT)"""
        try:
            logging.info("Syncing SAT catalogs (Anexo 20)...")
            
            # 1. Monedas
            df_monedas = pd.DataFrame([
                {"code": "MXN", "description": "Peso Mexicano", "decimals": 2},
                {"code": "USD", "description": "Dólar americano", "decimals": 2},
                {"code": "EUR", "description": "Euro", "decimals": 2},
                {"code": "XXX", "description": "Los códigos asignados para las transacciones en que no intervenga ninguna moneda", "decimals": 0}
            ])
            SCD2Manager(target_table="cat_monedas", natural_key="code", schema="fiscal").upsert(df_monedas)
            
            # 2. Formas de Pago
            df_forma = pd.DataFrame([
                {"code": "01", "description": "Efectivo", "bancarizado": False},
                {"code": "02", "description": "Cheque nominativo", "bancarizado": True},
                {"code": "03", "description": "Transferencia electrónica de fondos", "bancarizado": True},
                {"code": "04", "description": "Tarjeta de crédito", "bancarizado": True},
                {"code": "28", "description": "Tarjeta de débito", "bancarizado": True},
                {"code": "99", "description": "Por definir", "bancarizado": False}
            ])
            SCD2Manager(target_table="cat_forma_pago", natural_key="code", schema="fiscal").upsert(df_forma)
            
            # 3. Métodos de Pago
            df_metodo = pd.DataFrame([
                {"code": "PUE", "description": "Pago en una sola exhibición"},
                {"code": "PPD", "description": "Pago en parcialidades o diferido"}
            ])
            SCD2Manager(target_table="cat_metodo_pago", natural_key="code", schema="fiscal").upsert(df_metodo)
            
            # 4. Exportación
            df_exp = pd.DataFrame([
                {"code": "01", "description": "No aplica"},
                {"code": "02", "description": "Definitiva"},
                {"code": "03", "description": "Temporal"}
            ])
            SCD2Manager(target_table="cat_exportacion", natural_key="code", schema="fiscal").upsert(df_exp)
            
            # 5. Objeto Impuesto
            df_obj = pd.DataFrame([
                {"code": "01", "description": "No objeto de impuesto"},
                {"code": "02", "description": "Sí objeto de impuesto"},
                {"code": "03", "description": "Sí objeto de impuesto y no obligado al desglose"}
            ])
            SCD2Manager(target_table="cat_objeto_imp", natural_key="code", schema="fiscal").upsert(df_obj)
            
            # 6. Unidades de Medida
            df_unidades = pd.DataFrame([
                {"code": "H87", "name": "Pieza"},
                {"code": "E48", "name": "Unidad de servicio"},
                {"code": "KGM", "name": "Kilogramo"},
                {"code": "LTR", "name": "Litro"}
            ])
            SCD2Manager(target_table="cat_unidades", natural_key="code", schema="fiscal").upsert(df_unidades)
            
            # 7. Productos y Servicios (Top level / Common - Hierarchical)
            df_prod = pd.DataFrame([
                # Divisiones (Nivel 1: XX000000)
                {"code": "01000000", "description": "Difusión de material en vivo y en directo y animales y plantas vivos"},
                {"code": "84000000", "description": "Servicios profesionales, científicos y técnicos"},
                {"code": "43000000", "description": "Tecnología de la información, telecomunicaciones y entretenimiento"},
                {"code": "81000000", "description": "Servicios informáticos, consultoría y soporte de TI"},
                
                # Grupos (Nivel 2: XXXX0000)
                {"code": "01010000", "description": "Animales vivos"},
                {"code": "84110000", "description": "Servicios de contabilidad, auditoría y teneduría de libros"},
                {"code": "43230000", "description": "Software"},
                {"code": "81110000", "description": "Servicios informáticos y de soporte de TI"},
                
                # Clases (Nivel 3: XXXXXX00)
                {"code": "01010100", "description": "Perros de compañía vivos y gatos vivos"},
                {"code": "84111500", "description": "Servicios de contabilidad y auditoría general"},
                {"code": "43231500", "description": "Software de gestión empresarial"},
                {"code": "81111500", "description": "Sistemas y soporte de redes de computadoras"},
                
                # Productos (Nivel 4: XXXXXXXX)
                {"code": "01010101", "description": "Perros de compañía vivos"},
                {"code": "84111506", "description": "Servicios de facturación"},
                {"code": "81111504", "description": "Mantenimiento y soporte de software"}
            ])
            SCD2Manager(target_table="cat_prod_serv", natural_key="code", schema="fiscal").upsert(df_prod)
            
            # 8. Regímenes Fiscales
            df_regimen = pd.DataFrame([
                {"code": "601", "description": "General de Ley Personas Morales"},
                {"code": "603", "description": "Personas Morales con Fines no Lucrativos"},
                {"code": "605", "description": "Sueldos y Salarios e Ingresos Asimilados a Salarios"},
                {"code": "606", "description": "Arrendamiento"},
                {"code": "612", "description": "Personas Físicas con Actividades Empresariales y Profesionales"},
                {"code": "626", "description": "Régimen Simplificado de Confianza"}
            ])
            SCD2Manager(target_table="cat_regimen_fiscal", natural_key="code", schema="fiscal").upsert(df_regimen)
            
            # 9. Usos de CFDI
            df_uso = pd.DataFrame([
                {"code": "G01", "description": "Adquisición de mercancías"},
                {"code": "G03", "description": "Gastos en general"},
                {"code": "I01", "description": "Construcciones"},
                {"code": "S01", "description": "Sin efectos fiscales"},
                {"code": "CP01", "description": "Pagos"}
            ])
            SCD2Manager(target_table="cat_uso_cfdi", natural_key="code", schema="fiscal").upsert(df_uso)
            
            return {"status": "sat_catalogs_synced"}
        except Exception as e:
            logging.error(f"SAT sync failed: {e}")
            return {"error": str(e)}

    @staticmethod
    def sync_casfim():
        """Sync financial institutions (CASFIM) - Full PDF Extraction with robust fallback seeding"""
        try:
            from app.services.casfim_processor import CasfimProcessor
            processor = CasfimProcessor()
            html_path = "/app/casfim_links.html"
            
            logging.info("Starting full CASFIM sync from PDFs...")
            links = processor.get_links_from_html(html_path)
            links = processor.download_pdfs(links)
            processed = processor.process_with_docling(links)
            df = processor.extract_institutions(processed)
            
            logging.info(f"Extracted {len(df)} institutions from CASFIM PDFs.")
            return processor.load_to_db(df)
        except Exception as e:
            logging.error(f"CASFIM sync failed: {e}. Seeding default CASFIM catalog...")
            
            # Fallback Seeder: Inyecta bancos reales con estatus (activos, fusionados, cancelados)
            df_types = pd.DataFrame([
                {"nombre": "BANCA MÚLTIPLE"},
                {"nombre": "SOFIPO"},
                {"nombre": "IFPE"}
            ])
            manager_types = SCD2Manager(target_table="cat_entidad_tipos", natural_key="nombre", schema="financial")
            manager_types.upsert(df_types)
            
            with manager_types.engine.connect() as conn:
                type_map = {r[0]: r[1] for r in conn.execute(text("SELECT nombre, id FROM financial.cat_entidad_tipos WHERE scd_is_current = TRUE"))}
                
            bancos_data = [
                {"clave": "012", "nombre": "BBVA MÉXICO, S.A.", "corto": "BBVA", "tipo": "BANCA MÚLTIPLE", "estatus": "ACTIVA", "active": True},
                {"clave": "002", "nombre": "BANCO NACIONAL DE MÉXICO, S.A.", "corto": "BANAMEX", "tipo": "BANCA MÚLTIPLE", "estatus": "ACTIVA", "active": True},
                {"clave": "021", "nombre": "HSBC MÉXICO, S.A.", "corto": "HSBC", "tipo": "BANCA MÚLTIPLE", "estatus": "ACTIVA", "active": True},
                {"clave": "014", "nombre": "BANCO MERCANTIL DEL NORTE, S.A.", "corto": "BANORTE", "tipo": "BANCA MÚLTIPLE", "estatus": "ACTIVA", "active": True},
                {"clave": "036", "nombre": "BANCO INBURSA, S.A.", "corto": "INBURSA", "tipo": "BANCA MÚLTIPLE", "estatus": "ACTIVA", "active": True},
                {"clave": "044", "nombre": "SCOTIABANK INVERLAT, S.A.", "corto": "SCOTIABANK", "tipo": "BANCA MÚLTIPLE", "estatus": "ACTIVA", "active": True},
                {"clave": "127", "nombre": "BANCO AZTECA, S.A.", "corto": "BANCO AZTECA", "tipo": "BANCA MÚLTIPLE", "estatus": "ACTIVA", "active": True},
                {"clave": "137", "nombre": "BANCOPPEL, S.A.", "corto": "BANCOPPEL", "tipo": "BANCA MÚLTIPLE", "estatus": "ACTIVA", "active": True},
                {"clave": "652", "nombre": "NU MÉXICO FINANCIERA, S.A. DE C.V.", "corto": "NU MÉXICO", "tipo": "SOFIPO", "estatus": "ACTIVA", "active": True},
                {"clave": "684", "nombre": "KLU INTEGRACIÓN TECNOLÓGICA, S.A. DE C.V. (KLU)", "corto": "KLU", "tipo": "IFPE", "estatus": "ACTIVA", "active": True},
                # Fusionados / Cancelados
                {"clave": "086", "nombre": "BANCO BITAL, S.A. (AHORA HSBC)", "corto": "BITAL", "tipo": "BANCA MÚLTIPLE", "estatus": "FUSIONADA", "active": False},
                {"clave": "016", "nombre": "BANCO DEL ATLÁNTICO, S.A. (AHORA HSBC)", "corto": "ATLÁNTICO", "tipo": "BANCA MÚLTIPLE", "estatus": "FUSIONADA", "active": False},
                {"clave": "019", "nombre": "BANCO UNIÓN, S.A.", "corto": "BANCO UNIÓN", "tipo": "BANCA MÚLTIPLE", "estatus": "CANCELADA", "active": False}
            ]
            
            df_bancos = pd.DataFrame(bancos_data)
            df_bancos['tipo_entidad_id'] = df_bancos['tipo'].map(type_map)
            df_bancos = df_bancos.drop(columns=['tipo'])
            
            manager_inst = SCD2Manager(target_table="instituciones_bancarias", natural_key="clave", schema="financial")
            manager_inst.upsert(df_bancos)
            
            # Map Successors (Bital 086 y Atlántico 016 absorvidos por HSBC 021)
            with manager_inst.engine.connect() as conn:
                hsbc_id = conn.execute(text("SELECT id FROM financial.instituciones_bancarias WHERE clave = '021' AND scd_is_current = TRUE")).scalar()
                if hsbc_id:
                    conn.execute(text("UPDATE financial.instituciones_bancarias SET sucesora_id = :hsbc_id WHERE clave IN ('086', '016') AND scd_is_current = TRUE"), {"hsbc_id": hsbc_id})
                    
            logging.info("Fallback CASFIM seeding completed successfully.")
            return {"status": "seeded_fallback_casfim"}

    @staticmethod
    def sync_countries():
        """Sync global countries (ISO 3166)"""
        data = [
            {"iso_alpha3": "MEX", "iso_alpha2": "MX", "numeric_code": "484", "name": "México", "name_en": "Mexico", "name_fr": "Mexique", "name_native": "México", "phone_code": "+52"},
            {"iso_alpha3": "USA", "iso_alpha2": "US", "numeric_code": "840", "name": "Estados Unidos de América", "name_en": "United States of America", "name_fr": "États-Unis d'Amérique", "name_native": "United States", "phone_code": "+1"},
            {"iso_alpha3": "CAN", "iso_alpha2": "CA", "numeric_code": "124", "name": "Canadá", "name_en": "Canada", "name_fr": "Canada", "name_native": "Canada", "phone_code": "+1"},
            {"iso_alpha3": "ESP", "iso_alpha2": "ES", "numeric_code": "724", "name": "España", "name_en": "Spain", "name_fr": "Espagne", "name_native": "España", "phone_code": "+34"},
            {"iso_alpha3": "BRA", "iso_alpha2": "BR", "numeric_code": "076", "name": "Brasil", "name_en": "Brazil", "name_fr": "Brésil", "name_native": "Brasil", "phone_code": "+55"},
            {"iso_alpha3": "ARG", "iso_alpha2": "AR", "numeric_code": "032", "name": "Argentina", "name_en": "Argentina", "name_fr": "Argentine", "name_native": "Argentina", "phone_code": "+54"},
            {"iso_alpha3": "COL", "iso_alpha2": "CO", "numeric_code": "170", "name": "Colombia", "name_en": "Colombia", "name_fr": "Colombie", "name_native": "Colombia", "phone_code": "+57"},
            {"iso_alpha3": "CHL", "iso_alpha2": "CL", "numeric_code": "152", "name": "Chile", "name_en": "Chile", "name_fr": "Chili", "name_native": "Chile", "phone_code": "+56"},
            {"iso_alpha3": "GBR", "iso_alpha2": "GB", "numeric_code": "826", "name": "Reino Unido", "name_en": "United Kingdom", "name_fr": "Royaume-Uni", "name_native": "United Kingdom", "phone_code": "+44"},
            {"iso_alpha3": "FRA", "iso_alpha2": "FR", "numeric_code": "250", "name": "Francia", "name_en": "France", "name_fr": "France", "name_native": "France", "phone_code": "+33"},
            {"iso_alpha3": "DEU", "iso_alpha2": "DE", "numeric_code": "276", "name": "Alemania", "name_en": "Germany", "name_fr": "Allemagne", "name_native": "Deutschland", "phone_code": "+49"},
            {"iso_alpha3": "CHN", "iso_alpha2": "CN", "numeric_code": "156", "name": "China", "name_en": "China", "name_fr": "Chine", "name_native": "中国", "phone_code": "+86"},
            {"iso_alpha3": "JPN", "iso_alpha2": "JP", "numeric_code": "392", "name": "Japón", "name_en": "Japan", "name_fr": "Japon", "name_native": "日本", "phone_code": "+81"}
        ]
        df = pd.DataFrame(data)
        manager = SCD2Manager(target_table="paises", natural_key="iso_alpha3", schema="geo")
        return manager.upsert(df)

    @staticmethod
    def sync_geo_lookups(df_clean):
        """Sync lookup tables for settlement types and zones"""
        # Settlement Types
        types = df_clean['settlement_type'].unique()
        df_types = pd.DataFrame([{"name": t} for t in types if pd.notna(t)])
        manager_types = SCD2Manager(target_table="asentamiento_tipos", natural_key="name", schema="geo")
        manager_types.upsert(df_types)
        
        # Zone Types
        zones = df_clean['zone_type'].unique()
        df_zones = pd.DataFrame([{"name": z} for z in zones if pd.notna(z)])
        manager_zones = SCD2Manager(target_table="zona_tipos", natural_key="name", schema="geo")
        manager_zones.upsert(df_zones)

    @staticmethod
    def sync_sepomex_local():
        """Process local SEPOMEX files with strictly normalized hierarchy"""
        CatalogDownloader.sync_countries()
        
        sepomex_path = "/app/sepomex/CPdescarga.txt"
        if not os.path.exists(sepomex_path):
            sepomex_path = "/home/ia/ecosistema-casmarts/sepomex/CPdescarga.txt"
            if not os.path.exists(sepomex_path):
                return {"error": "SEPOMEX source file not found"}
            
        logging.info(f"Processing SEPOMEX file: {sepomex_path}")
        df = pd.read_csv(sepomex_path, sep="|", encoding="latin-1")
        
        df_clean = df.rename(columns={
            "d_codigo": "cp",
            "d_asenta": "name",
            "d_tipo_asenta": "settlement_type",
            "D_mnpio": "municipality_name",
            "d_estado": "state_name",
            "c_estado": "state_code",
            "c_mnpio": "municipality_code",
            "d_zona": "zone_type"
        })
        
        df_clean['cp'] = df_clean['cp'].astype(str).str.zfill(5)
        df_clean['state_code'] = df_clean['state_code'].astype(str).str.zfill(2)
        df_clean['municipality_code'] = df_clean['municipality_code'].astype(str).str.zfill(3)
        
        # 1. Sync Lookups
        CatalogDownloader.sync_geo_lookups(df_clean)
        
        # Get Maps
        manager = SCD2Manager(target_table="paises", natural_key="iso_alpha3", schema="geo")
        with manager.engine.connect() as conn:
            mex_id = conn.execute(text("SELECT id FROM geo.paises WHERE iso_alpha3 = 'MEX' AND scd_is_current = TRUE")).scalar()
            type_map = {r[0]: r[1] for r in conn.execute(text("SELECT name, id FROM geo.asentamiento_tipos"))}
            zone_map = {r[0]: r[1] for r in conn.execute(text("SELECT name, id FROM geo.zona_tipos"))}

        # 2. Sync Estados
        df_estados = df_clean[['state_code', 'state_name']].drop_duplicates()
        df_estados = df_estados.rename(columns={'state_name': 'name'})
        df_estados['country_id'] = mex_id
        manager_estados = SCD2Manager(target_table="estados", natural_key="state_code", schema="geo")
        manager_estados.upsert(df_estados)
        
        # 3. Sync Municipios
        with manager.engine.connect() as conn:
            states_map = {r[0]: r[1] for r in conn.execute(text("SELECT state_code, id FROM geo.estados WHERE scd_is_current = TRUE"))}
        
        df_mun = df_clean[['state_code', 'municipality_code', 'municipality_name']].drop_duplicates()
        df_mun = df_mun.rename(columns={'municipality_name': 'name'})
        df_mun['state_id'] = df_mun['state_code'].map(states_map)
        manager_mun = SCD2Manager(target_table="municipios", natural_key=["state_id", "municipality_code"], schema="geo")
        manager_mun.upsert(df_mun.drop(columns=['state_code']))

        # 4. Sync CPs
        df_cp = df_clean[['cp']].drop_duplicates()
        manager_cp = SCD2Manager(target_table="codigos_postales", natural_key="cp", schema="geo")
        manager_cp.upsert(df_cp)
        
        # 5. Sync Asentamientos
        with manager.engine.connect() as conn:
            mun_res = conn.execute(text("SELECT id, state_id, municipality_code FROM geo.municipios WHERE scd_is_current = TRUE")).fetchall()
            mun_df = pd.DataFrame([{"municipality_id": r[0], "state_id": str(r[1]), "municipality_code": str(r[2])} for r in mun_res])
            cp_map = {r[1]: r[0] for r in conn.execute(text("SELECT id, cp FROM geo.codigos_postales WHERE scd_is_current = TRUE"))}

        df_asenta = df_clean[['state_code', 'municipality_code', 'cp', 'name', 'settlement_type', 'zone_type']].drop_duplicates()
        df_asenta['state_id'] = df_asenta['state_code'].map(states_map).astype(str)
        df_asenta['municipality_code'] = df_asenta['municipality_code'].astype(str)
        
        logging.info(f"Mapping asentamientos... Rows: {len(df_asenta)}")
        df_asenta = df_asenta.merge(mun_df, on=['state_id', 'municipality_code'], how='left')
        logging.info(f"After mun merge: {len(df_asenta)}. NaNs: {df_asenta['municipality_id'].isna().sum()}")
        
        df_asenta['cp_id'] = df_asenta['cp'].map(cp_map)
        logging.info(f"CP Map sample: {list(cp_map.items())[:3]}")
        logging.info(f"DF CP sample: {df_asenta['cp'].head(3).tolist()}")
        logging.info(f"DF CP types: {df_asenta['cp'].apply(type).unique()}")
        logging.info(f"After CP map. NaNs: {df_asenta['cp_id'].isna().sum()}")
        
        df_asenta['asentamiento_tipo_id'] = df_asenta['settlement_type'].map(type_map)
        df_asenta['zona_tipo_id'] = df_asenta['zone_type'].map(zone_map)
        
        df_asenta_final = df_asenta[['municipality_id', 'cp_id', 'asentamiento_tipo_id', 'zona_tipo_id', 'name']].dropna()
        logging.info(f"Final records to insert: {len(df_asenta_final)}")
        
        df_asenta_final['municipality_id'] = df_asenta_final['municipality_id'].astype(str)
        df_asenta_final['cp_id'] = df_asenta_final['cp_id'].astype(str)
        df_asenta_final['asentamiento_tipo_id'] = df_asenta_final['asentamiento_tipo_id'].astype(str)
        df_asenta_final['zona_tipo_id'] = df_asenta_final['zona_tipo_id'].astype(str)
        
        manager_asenta = SCD2Manager(target_table="asentamientos", natural_key=["municipality_id", "cp_id", "name"], schema="geo")
        manager_asenta.upsert(df_asenta_final)
        
        return {"status": "sepomex_normalized_synced", "count": len(df_asenta_final)}

    @staticmethod
    def sync_holidays(year: int = None):
        if not year:
            year = date.today().year
            
        mx_holidays = holidays.MX(years=year)
        
        translation_map = {
            "New Year's Day": "Año Nuevo",
            "Constitution Day": "Día de la Constitución",
            "Benito Juárez's Birthday": "Natalicio de Benito Juárez",
            "Maundy Thursday": "Jueves Santo",
            "Good Friday": "Viernes Santo",
            "Labor Day": "Día del Trabajo",
            "Independence Day": "Día de la Independencia",
            "Revolution Day": "Día de la Revolución",
            "Change of Federal Government": "Transmisión del Poder Ejecutivo Federal",
            "Christmas Day": "Navidad",
            "Day of the Dead": "Día de Muertos",
            "Our Lady of Guadalupe": "Día de la Virgen de Guadalupe"
        }
        
        data = []
        for dt, name in mx_holidays.items():
            translated_name = translation_map.get(name, name)
            data.append({
                "date": dt.isoformat(),
                "name": translated_name,
                "country_code": "MX"
            })
            
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date']).dt.date
        manager = SCD2Manager(target_table="holidays", natural_key="date", schema="calendars")
        return manager.upsert(df)
