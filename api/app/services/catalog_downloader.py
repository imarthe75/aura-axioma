import holidays
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import logging
from sqlalchemy import text
from app.services.scd2_manager import SCD2Manager
from app.core.celery_app import celery_app
import zipfile
import io
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
                {"code": "43000000", "description": "Tecnología de la información, telecomunicaciones y entretenimiento"},
                {"code": "81000000", "description": "Servicios informáticos, consultoría y soporte de TI"},
                {"code": "84000000", "description": "Servicios profesionales, científicos y técnicos"},
                {"code": "80000000", "description": "Servicios de consultoría de gestión y servicios empresariales"},
                {"code": "86000000", "description": "Servicios de educación y capacitación"},
                
                # Grupos (Nivel 2: XXXX0000)
                {"code": "01010000", "description": "Animales vivos"},
                {"code": "43230000", "description": "Software"},
                {"code": "43220000", "description": "Equipos y servicios de red y telecomunicaciones"},
                {"code": "81110000", "description": "Servicios informáticos y de soporte de TI"},
                {"code": "84110000", "description": "Servicios de contabilidad, auditoría y teneduría de libros"},
                {"code": "84130000", "description": "Servicios de marketing, publicidad y relaciones públicas"},
                {"code": "80100000", "description": "Servicios de consultoría de gestión empresarial"},
                {"code": "86100000", "description": "Servicios de educación y escuelas"},
                
                # Clases (Nivel 3: XXXXXX00)
                {"code": "01010100", "description": "Perros de compañía vivos y gatos vivos"},
                {"code": "43231500", "description": "Software de gestión empresarial"},
                {"code": "43231600", "description": "Software de sistema operativo y utilidades"},
                {"code": "43232100", "description": "Software de desarrollo de aplicaciones"},
                {"code": "43232600", "description": "Software de diseño y multimedia"},
                {"code": "43221700", "description": "Equipos de red fija y conmutación"},
                {"code": "43222500", "description": "Servicios de telecomunicaciones"},
                {"code": "81111500", "description": "Sistemas y soporte de redes de computadoras"},
                {"code": "81111800", "description": "Servicios de computación en la nube"},
                {"code": "81112000", "description": "Servicios de desarrollo de software y sistemas"},
                {"code": "84111500", "description": "Servicios de contabilidad y auditoría general"},
                {"code": "84131500", "description": "Servicios de publicidad y campañas integrales"},
                {"code": "80101500", "description": "Servicios de consultoría y asesoría empresarial"},
                {"code": "86101700", "description": "Servicios educativos de nivel superior"},
                
                # Productos (Nivel 4: XXXXXXXX)
                {"code": "01010101", "description": "Perros de compañía vivos"},
                {"code": "01010102", "description": "Gatos vivos"},
                {"code": "43231501", "description": "Software de gestión de relaciones con clientes CRM"},
                {"code": "43231502", "description": "Software de planificación de recursos empresariales ERP"},
                {"code": "43231503", "description": "Software de inteligencia empresarial y análisis"},
                {"code": "43231504", "description": "Software de gestión de cadena de suministro SCM"},
                {"code": "43231505", "description": "Software de gestión de recursos humanos HRMS"},
                {"code": "43231506", "description": "Software de facturación y contabilidad"},
                {"code": "43231507", "description": "Software de gestión de proyectos y colaboración"},
                {"code": "43231601", "description": "Sistemas operativos de servidor"},
                {"code": "43231602", "description": "Software de base de datos"},
                {"code": "43231603", "description": "Software de seguridad y antivirus"},
                {"code": "43231604", "description": "Software de virtualización"},
                {"code": "43232101", "description": "Entornos de desarrollo integrados IDE"},
                {"code": "43232102", "description": "Compiladores y depuradores"},
                {"code": "43232601", "description": "Software de diseño asistido por computadora CAD"},
                {"code": "43232602", "description": "Software de edición gráfica y modelado 3D"},
                {"code": "43221701", "description": "Ruteadores y switches de comunicación"},
                {"code": "43221702", "description": "Servidores de acceso de red y cortafuegos de hardware"},
                {"code": "43222501", "description": "Servicio de internet de banda ancha de fibra óptica"},
                {"code": "43222502", "description": "Servicios de telefonía IP VOIP empresarial"},
                {"code": "81111501", "description": "Servicios de administración y monitoreo de red remota"},
                {"code": "81111502", "description": "Instalación de hardware y cableado estructurado certificado"},
                {"code": "81111503", "description": "Servicios de auditoría de seguridad informática y cortafuegos de red"},
                {"code": "81111504", "description": "Mantenimiento y soporte de software de infraestructura de red"},
                {"code": "81111801", "description": "Servicios de hosting y alojamiento web dedicado de alta velocidad"},
                {"code": "81111802", "description": "Almacenamiento y respaldo en la nube automatizado (SaaS)"},
                {"code": "81111803", "description": "Servicios de infraestructura como servicio (IaaS) elástica"},
                {"code": "81112001", "description": "Desarrollo a la medida de páginas web y aplicaciones móviles nativas"},
                {"code": "81112002", "description": "Diseño, optimización y arquitectura de bases de datos relacionales"},
                {"code": "81112003", "description": "Servicios de integración avanzada de sistemas de TI empresariales"},
                {"code": "84111501", "description": "Servicios integrales de teneduría de libros y registros de contabilidad"},
                {"code": "84111502", "description": "Servicios de preparación, cálculo y declaración de impuestos anuales"},
                {"code": "84111503", "description": "Servicios de auditoría fiscal externa e interna"},
                {"code": "84111506", "description": "Servicios de facturación electrónica y emisión de CFDI autorizados"},
                {"code": "84131501", "description": "Diseño conceptual de campañas publicitarias digitales e impresas"},
                {"code": "84131502", "description": "Gestión estratégica de redes sociales y marketing digital (SEO/SEM)"},
                {"code": "84131503", "description": "Servicios de colocación y compra de espacios publicitarios en medios"},
                {"code": "80101501", "description": "Servicios de consultoría en desarrollo organizacional y cultura corporativa"},
                {"code": "80101502", "description": "Servicios de planificación y consultoría estratégica empresarial"},
                {"code": "80101503", "description": "Servicios de consultoría en gestión de riesgos corporativos"},
                {"code": "86101701", "description": "Servicios educativos universitarios presenciales licenciaturas e ingenierías"},
                {"code": "86101702", "description": "Servicios de capacitación profesional continua y certificaciones en línea"}
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
            
            # 10. Bancos del SAT (c_Banco)
            df_bancos = pd.DataFrame([
                {"code": "002", "nombre_corto": "BANAMEX", "razon_social": "Banco Nacional de México, S.A.", "rfc": "BNM840515VB1"},
                {"code": "012", "nombre_corto": "BBVA", "razon_social": "BBVA México, S.A.", "rfc": "BBA830831LJ8"},
                {"code": "014", "nombre_corto": "SANTANDER", "razon_social": "Banco Santander México, S.A.", "rfc": "BSM970519DU8"},
                {"code": "021", "nombre_corto": "HSBC", "razon_social": "HSBC México, S.A.", "rfc": "HME9501258M1"},
                {"code": "030", "nombre_corto": "BAJIO", "razon_social": "Banco del Bajío, S.A.", "rfc": "BBA940707IE1"},
                {"code": "036", "nombre_corto": "INBURSA", "razon_social": "Banco Inbursa, S.A.", "rfc": "BIN9310115V9"},
                {"code": "044", "nombre_corto": "SCOTIABANK", "razon_social": "Scotiabank Inverlat, S.A.", "rfc": "SIN9412025I4"},
                {"code": "072", "nombre_corto": "BANORTE", "razon_social": "Banco Mercantil del Norte, S.A.", "rfc": "BMN930209927"},
                {"code": "112", "nombre_corto": "BANCO AZTECA", "razon_social": "Banco Azteca, S.A.", "rfc": "BAZ0206187T0"},
                {"code": "127", "nombre_corto": "COMPARTAMOS", "razon_social": "Banco Compartamos, S.A.", "rfc": "BCO0208269S8"},
                {"code": "137", "nombre_corto": "BANREGIO", "razon_social": "Banco Regional, S.A.", "rfc": "BRE9402283R7"},
                {"code": "901", "nombre_corto": "CLN", "razon_social": "Clabe Interbancaria Extranjera", "rfc": "XXX000000XXX"}
            ])
            SCD2Manager(target_table="cat_bancos", natural_key="code", schema="fiscal").upsert(df_bancos)

            # 11. Países del SAT (c_Pais)
            df_paises = pd.DataFrame([
                {"code": "MEX", "description": "México", "agrupacion": "América del Norte"},
                {"code": "USA", "description": "Estados Unidos de América", "agrupacion": "América del Norte"},
                {"code": "CAN", "description": "Canadá", "agrupacion": "América del Norte"},
                {"code": "DEU", "description": "Alemania", "agrupacion": "Europa"},
                {"code": "ESP", "description": "España", "agrupacion": "Europa"},
                {"code": "FRA", "description": "Francia", "agrupacion": "Europa"},
                {"code": "GBR", "description": "Reino Unido", "agrupacion": "Europa"},
                {"code": "CHN", "description": "China", "agrupacion": "Asia"},
                {"code": "JPN", "description": "Japón", "agrupacion": "Asia"},
                {"code": "BRA", "description": "Brasil", "agrupacion": "América del Sur"},
                {"code": "ARG", "description": "Argentina", "agrupacion": "América del Sur"}
            ])
            SCD2Manager(target_table="cat_paises", natural_key="code", schema="fiscal").upsert(df_paises)
            
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
            manager_inst = SCD2Manager(target_table="instituciones_bancarias", natural_key=["clave", "tipo_entidad_id"], schema="financial")
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
    def download_sepomex_latest():
        """Download latest SEPOMEX ZIP from Correos de México and extract the text file"""
        url = 'https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        logging.info("Downloading latest SEPOMEX ZIP from official site...")
        try:
            session = requests.Session()
            # 1. GET request to obtain current ASP.NET ViewState parameters
            r_get = session.get(url, headers=headers, verify=False, timeout=30)
            soup = BeautifulSoup(r_get.text, 'html.parser')
            
            vs = soup.find('input', id='__VIEWSTATE').get('value')
            vsg = soup.find('input', id='__VIEWSTATEGENERATOR').get('value')
            ev = soup.find('input', id='__EVENTVALIDATION').get('value')
            
            # 2. Build form payload
            payload = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': vs,
                '__VIEWSTATEGENERATOR': vsg,
                '__EVENTVALIDATION': ev,
                'cboEdo': '00',          # Todos (All states)
                'rblTipo': 'txt',        # TXT format
                'btnDescarga.x': '15',   # ASP.NET image coordinates
                'btnDescarga.y': '15'
            }
            
            # 3. POST request to submit form and download the ZIP file content
            r_post = session.post(url, data=payload, headers=headers, verify=False, timeout=60)
            if r_post.status_code == 200 and "CPdescargatxt" in r_post.headers.get('Content-Disposition', ''):
                zip_file = zipfile.ZipFile(io.BytesIO(r_post.content))
                
                # Locate the .txt file inside the ZIP archive
                txt_filename = None
                for name in zip_file.namelist():
                    if name.endswith('.txt'):
                        txt_filename = name
                        break
                
                if txt_filename:
                    target_dir = "/app/sepomex"
                    os.makedirs(target_dir, exist_ok=True)
                    target_file = os.path.join(target_dir, "CPdescarga.txt")
                    
                    with open(target_file, "wb") as f_out:
                        f_out.write(zip_file.read(txt_filename))
                        
                    logging.info(f"Successfully downloaded and extracted {txt_filename} to {target_file}")
                    return True
                else:
                    logging.error("No .txt file found inside SEPOMEX ZIP archive.")
            else:
                logging.error(f"Failed to retrieve SEPOMEX ZIP. Server responded with status code: {r_post.status_code}")
        except Exception as e:
            logging.error(f"Error downloading latest SEPOMEX ZIP: {e}")
        return False

    @staticmethod
    def sync_sepomex_local():
        """Process local SEPOMEX files with strictly normalized hierarchy"""
        CatalogDownloader.sync_countries()
        
        # Proactivamente descargar la versión más reciente de SEPOMEX
        CatalogDownloader.download_sepomex_latest()
        
        sepomex_path = "/app/sepomex/CPdescarga.txt"
        if not os.path.exists(sepomex_path):
            sepomex_path = "/home/ia/ecosistema-casmarts/sepomex/CPdescarga.txt"
            if not os.path.exists(sepomex_path):
                return {"error": "SEPOMEX source file not found"}
            
        logging.info(f"Processing SEPOMEX file: {sepomex_path}")
        # Auto-detect if line 1 is a copyright notice (Correos de México now includes it)
        # If the first line does NOT contain 'd_codigo', skip it (it's the legal notice)
        with open(sepomex_path, 'r', encoding='latin-1') as _f:
            _first_line = _f.readline()
        _skiprows = 1 if 'd_codigo' not in _first_line else 0
        if _skiprows:
            logging.info("Detected copyright notice on line 1 - skipping it.")
        df = pd.read_csv(sepomex_path, sep="|", encoding="latin-1", skiprows=_skiprows, low_memory=False)
        
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
        
        # self-contained Easter calculation (Meeus/Jones/Butcher)
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        easter_sunday = date(year, month, day)
        
        jueves_santo = easter_sunday - timedelta(days=3)
        viernes_santo = easter_sunday - timedelta(days=2)
        
        translation_map = {
            "new year's day": "Año Nuevo",
            "constitution day": "Día de la Constitución",
            "benito juárez's birthday": "Natalicio de Benito Juárez",
            "labor day": "Día del Trabajo",
            "independence day": "Día de la Independencia",
            "revolution day": "Día de la Revolución",
            "change of federal government": "Transmisión del Poder Ejecutivo Federal",
            "christmas day": "Navidad",
            "maundy thursday": "Jueves Santo",
            "good friday": "Viernes Santo",
            "day of the dead": "Día de Muertos",
            "our lady of guadalupe": "Día de la Virgen de Guadalupe"
        }
        
        registered_dates = set()
        data = []
        
        for dt, name in mx_holidays.items():
            clean_name = name.lower().strip()
            translated_name = translation_map.get(clean_name, name)
            
            data.append({
                "date": dt,
                "name": translated_name,
                "country_code": "MX",
                "metadata": {
                    "type": "official",
                    "origin": "holidays_package",
                    "is_lft_mandatory": True
                }
            })
            registered_dates.add(dt)
            
        # Add Jueves Santo and Viernes Santo explicitly if they aren't registered
        for holiday_date, name in [(jueves_santo, "Jueves Santo"), (viernes_santo, "Viernes Santo")]:
            if holiday_date not in registered_dates:
                data.append({
                    "date": holiday_date,
                    "name": name,
                    "country_code": "MX",
                    "metadata": {
                        "type": "banking",
                        "origin": "cnbv_custom",
                        "is_lft_mandatory": False
                    }
                })
                registered_dates.add(holiday_date)
                
        # Add Día de Muertos (Nov 2) and Virgen de Guadalupe (Dec 12) explicitly as banking holidays
        for m_day, m_month, name in [(2, 11, "Día de Muertos"), (12, 12, "Día de la Virgen de Guadalupe")]:
            holiday_date = date(year, m_month, m_day)
            if holiday_date not in registered_dates:
                data.append({
                    "date": holiday_date,
                    "name": name,
                    "country_code": "MX",
                    "metadata": {
                        "type": "banking",
                        "origin": "cnbv_custom",
                        "is_lft_mandatory": False
                    }
                })
                registered_dates.add(holiday_date)

        # Inject official vacation periods
        # Semana Santa Vacation: Monday of Holy Week to Sunday of Easter Week (14 days)
        ss_start = jueves_santo - timedelta(days=3)
        for i in range(14):
            vac_date = ss_start + timedelta(days=i)
            if vac_date not in registered_dates:
                data.append({
                    "date": vac_date,
                    "name": "Período Vacacional - Semana Santa",
                    "country_code": "MX",
                    "metadata": {
                        "type": "vacation",
                        "origin": "sep_schedule",
                        "is_lft_mandatory": False
                    }
                })
                
        # Summer Vacations (July 15 to Aug 15)
        summer_start = date(year, 7, 15)
        for i in range(32):
            vac_date = summer_start + timedelta(days=i)
            if vac_date not in registered_dates:
                data.append({
                    "date": vac_date,
                    "name": "Período Vacacional - Verano",
                    "country_code": "MX",
                    "metadata": {
                        "type": "vacation",
                        "origin": "sep_schedule",
                        "is_lft_mandatory": False
                    }
                })
                
        # Winter Vacations (Dec 18 to Jan 8 next year)
        winter_start = date(year, 12, 18)
        for i in range(22):
            vac_date = winter_start + timedelta(days=i)
            if vac_date not in registered_dates:
                data.append({
                    "date": vac_date,
                    "name": "Período Vacacional - Fin de Año",
                    "country_code": "MX",
                    "metadata": {
                        "type": "vacation",
                        "origin": "sep_schedule",
                        "is_lft_mandatory": False
                    }
                })
        
        df = pd.DataFrame(data)
        import json
        df['metadata'] = df['metadata'].apply(lambda x: json.dumps(x))
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        manager = SCD2Manager(target_table="holidays", natural_key="date", schema="calendars")
        return manager.upsert(df)
