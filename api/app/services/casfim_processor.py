import os
import requests
import re
import logging
from bs4 import BeautifulSoup
import pandas as pd
from app.services.scd2_manager import SCD2Manager
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)

class CasfimProcessor:
    BASE_URL = "https://www.gob.mx"
    DATA_DIR = "/app/data/casfim" if os.path.exists("/app/data") else "/home/ia/ecosistema-casmarts/aura-axioma/data/casfim"
    PDF_DIR = os.path.join(DATA_DIR, "pdfs")
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

    def __init__(self):
        print(f"Initializing CasfimProcessor. Data dir: {self.DATA_DIR}")
        os.makedirs(self.PDF_DIR, exist_ok=True)
        os.makedirs(self.PROCESSED_DIR, exist_ok=True)

    def get_links_from_html(self, html_path):
        """Extract sector names and PDF links from HTML"""
        print(f"Parsing links from {html_path}")
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        links = []
        
        # Pattern 1: Blockquotes (Sector 01, etc.)
        for p in soup.find_all('p'):
            if "Sector" in p.text:
                sector_text = p.text.strip()
                # Find the next blockquote with a link
                bq = p.find_next_sibling('blockquote')
                if bq:
                    a = bq.find('a')
                    if a and a.get('href'):
                        href = a['href']
                        if not href.startswith('http'):
                            href = self.BASE_URL + href
                        sector_name = a.text.strip()
                        links.append({
                            "sector_id": sector_text,
                            "sector_name": sector_name,
                            "url": href
                        })
        
        # Pattern 2: List items (Sector 53, etc.)
        for li in soup.find_all('li', class_='documents'):
            div_name = li.find('div', style=lambda x: x and 'capitalize' in x)
            if div_name:
                sector_id = div_name.text.strip()
                a = li.find('a', class_='btn-default')
                if a and a.get('href'):
                    href = a['href']
                    if not href.startswith('http'):
                        href = self.BASE_URL + href
                    links.append({
                        "sector_id": sector_id,
                        "sector_name": sector_id, # Fallback
                        "url": href
                    })
        
        return links

    def download_pdfs(self, links):
        """Download PDFs locally"""
        for item in links:
            filename = f"{item['sector_id'].replace(' ', '_')}.pdf"
            path = os.path.join(self.PDF_DIR, filename)
            if not os.path.exists(path):
                logging.info(f"Downloading {item['url']}...")
                try:
                    response = requests.get(item['url'], timeout=30)
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    item['local_path'] = path
                except Exception as e:
                    logging.error(f"Failed to download {item['url']}: {e}")
            else:
                item['local_path'] = path
        return links

    def process_with_docling(self, links):
        """Convert PDFs to markdown using docling REST API"""
        processed_data = []
        for item in links:
            if 'local_path' not in item: continue
            
            output_name = f"{item['sector_id'].replace(' ', '_')}.md"
            output_path = os.path.join(self.PROCESSED_DIR, output_name)
            
            if not os.path.exists(output_path):
                logging.info(f"Processing {item['local_path']} via Docling REST API...")
                try:
                    with open(item['local_path'], 'rb') as f:
                        files = {'files': (os.path.basename(item['local_path']), f, 'application/pdf')}
                        response = requests.post(
                            "http://casmarts-core-docling:5001/v1/convert/file",
                            files=files,
                            timeout=180
                        )
                    
                    if response.status_code == 200:
                        res_json = response.json()
                        markdown = res_json.get("document", {}).get("md_content") or ""
                        with open(output_path, 'w', encoding='utf-8') as f_out:
                            f_out.write(markdown)
                        logging.info(f"Successfully processed {item['local_path']} via Docling REST API.")
                    else:
                        logging.error(f"Docling REST API failed for {item['local_path']} with status {response.status_code}: {response.text}")
                        continue
                except Exception as e:
                    logging.error(f"Docling API connection failed for {item['local_path']}: {e}")
                    continue
            
            item['markdown_path'] = output_path
            processed_data.append(item)
        return processed_data

    def extract_institutions(self, processed_data):
        """Extract records from markdown files"""
        all_institutions = []
        
        for item in processed_data:
            logging.info(f"Extracting from {item['markdown_path']} (Sector: {item['sector_name']})")
            
            # Normalize sector name to include the number, e.g., "01 - Autoridades y Organismos Reguladores"
            sector_id_num = ""
            m = re.search(r'Sector\s*(\d+)', item['sector_id'], re.IGNORECASE)
            if m:
                sector_id_num = m.group(1).zfill(2)
            else:
                m2 = re.search(r'sector\s*(\d+)', item['markdown_path'], re.IGNORECASE)
                if m2:
                    sector_id_num = m2.group(1).zfill(2)
            
            if sector_id_num:
                # Capitalize first letter of each word in sector name for premium display
                raw_name = item['sector_name'].strip()
                words = raw_name.split()
                if words:
                    words = [w[0].upper() + w[1:] if len(w) > 0 else w for w in words]
                    clean_name = " ".join(words)
                else:
                    clean_name = raw_name
                sector_full_name = f"{sector_id_num} - {clean_name}"
            else:
                sector_full_name = item['sector_name'].upper()

            with open(item['markdown_path'], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            last_inst = None
            for line in lines:
                line_str = line.strip()
                if not line_str.startswith('|') or not line_str.endswith('|'):
                    continue
                # Split cells
                cells = [c.strip() for c in line_str.split('|')[1:-1]]
                if not cells:
                    continue
                
                # Check if it is a separator line (e.g. |---|---|)
                if all(re.match(r'^[\s\-:]*$', c) for c in cells):
                    continue
                
                # Check if first cell is header (e.g. "Clave", "Sector")
                if cells[0].lower() in ("clave", "sector"):
                    continue
                
                clave_raw = cells[0]
                # Normalize Clave (e.g., 40-012 -> 012)
                clave = clave_raw.split('-')[-1] if '-' in clave_raw else clave_raw
                
                if clave.isdigit() and len(clave) == 3:
                    nombre = cells[1] if len(cells) > 1 else ""
                    corto = cells[2] if len(cells) > 2 else ""
                    estatus = cells[3] if len(cells) > 3 else ""
                    
                    # Normalize name and short name
                    nombre_clean = " ".join(nombre.split())
                    corto_clean = " ".join(corto.split()) if corto.strip() else nombre_clean[:20]
                    
                    # Default active to True if no status column, else check status
                    active = True
                    if estatus:
                        active = "Operación" in estatus or "Autorizada" in estatus
                        
                    last_inst = {
                        "clave": clave,
                        "nombre": nombre_clean,
                        "tipo": sector_full_name,
                        "corto": corto_clean,
                        "active": active
                    }
                    all_institutions.append(last_inst)
                elif last_inst and not clave_raw:
                    # Handle split rows (append wrap-around text from Docling)
                    if len(cells) > 1 and cells[1]:
                        last_inst["nombre"] = " ".join((last_inst["nombre"] + " " + cells[1]).split())
                    if len(cells) > 2 and cells[2]:
                        # If current short name is just a placeholder, replace it. Otherwise append.
                        val = cells[2].strip()
                        if val:
                            if last_inst["corto"] == last_inst["nombre"][:20] or not last_inst["corto"]:
                                last_inst["corto"] = val
                            else:
                                last_inst["corto"] = " ".join((last_inst["corto"] + " " + val).split())
        
        df = pd.DataFrame(all_institutions)
        if not df.empty:
            # Sort by active first so duplicates keep the active one if any
            df = df.sort_values('active', ascending=False).drop_duplicates(subset=['clave', 'tipo'], keep='first')
        return df

    def load_to_db(self, df):
        """Load extracted data using SCD2Manager"""
        if df.empty:
            logging.warning("No data extracted to load.")
            return
        
        # 1. Sync Entity Types
        types = df['tipo'].unique()
        df_types = pd.DataFrame([{"nombre": t} for t in types])
        manager_types = SCD2Manager(target_table="cat_entidad_tipos", natural_key="nombre", schema="financial")
        manager_types.upsert(df_types)
        
        # 2. Get ID Maps
        with manager_types.engine.connect() as conn:
            type_map = {r[0]: r[1] for r in conn.execute(text("SELECT nombre, id FROM financial.cat_entidad_tipos WHERE scd_is_current = TRUE"))}
        
        # 3. Sync Institutions
        df['tipo_entidad_id'] = df['tipo'].map(type_map)
        df_final = df.drop(columns=['tipo']).drop_duplicates(subset=['clave', 'tipo_entidad_id'])
        
        manager_inst = SCD2Manager(target_table="instituciones_bancarias", natural_key=["clave", "tipo_entidad_id"], schema="financial")
        return manager_inst.upsert(df_final)

if __name__ == "__main__":
    processor = CasfimProcessor()
    html_path = "/app/casfim_links.html"
    links = processor.get_links_from_html(html_path)
    links = processor.download_pdfs(links)
    processed = processor.process_with_docling(links)
    df = processor.extract_institutions(processed)
    logging.info(f"Extracted {len(df)} institutions.")
    processor.load_to_db(df)
