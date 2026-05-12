import os
import requests
import re
import logging
from bs4 import BeautifulSoup
import pandas as pd
from docling.document_converter import DocumentConverter
from app.services.scd2_manager import SCD2Manager
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)

class CasfimProcessor:
    BASE_URL = "https://www.gob.mx"
    DATA_DIR = "/home/ia/ecosistema-casmarts/aura-axioma/data/casfim"
    PDF_DIR = os.path.join(DATA_DIR, "pdfs")
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

    def __init__(self):
        print(f"Initializing CasfimProcessor. Data dir: {self.DATA_DIR}")
        os.makedirs(self.PDF_DIR, exist_ok=True)
        os.makedirs(self.PROCESSED_DIR, exist_ok=True)
        self.converter = DocumentConverter()

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
        """Convert PDFs to markdown using docling"""
        processed_data = []
        for item in links:
            if 'local_path' not in item: continue
            
            output_name = f"{item['sector_id'].replace(' ', '_')}.md"
            output_path = os.path.join(self.PROCESSED_DIR, output_name)
            
            if not os.path.exists(output_path):
                logging.info(f"Processing {item['local_path']} with Docling...")
                try:
                    result = self.converter.convert(item['local_path'])
                    markdown = result.document.export_to_markdown()
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(markdown)
                except Exception as e:
                    logging.error(f"Docling failed for {item['local_path']}: {e}")
                    continue
            
            item['markdown_path'] = output_path
            processed_data.append(item)
        return processed_data

    def extract_institutions(self, processed_data):
        """Extract records from markdown files"""
        all_institutions = []
        
        for item in processed_data:
            logging.info(f"Extracting from {item['markdown_path']} (Sector: {item['sector_name']})")
            with open(item['markdown_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern for 5-column table: | Clave | Razón Social | Nombre Corto | Estatus | ... |
            # We use a more robust regex for markdown tables
            rows = re.findall(r'\|\s*([0-9\-]+)\s*\|\s*([^\|]+)\s*\|\s*([^\|]*)\s*\|\s*([^\|]*)\s*\|', content)
            
            if not rows:
                # Fallback to simple list if table parsing fails
                rows = re.findall(r'^\s*(\d{2,3}-\d{3})\s+([A-Z0-9\.\, ].+)$', content, re.MULTILINE)
                # Reformat to match expected structure
                rows = [(r[0], r[1], r[1][:20], "En Operación") for r in rows]

            for row in rows:
                clave_raw, nombre, corto, estatus = [r.strip() for r in row]
                
                # Normalize Clave (e.g., 40-012 -> 012)
                clave = clave_raw.split('-')[-1] if '-' in clave_raw else clave_raw
                if len(clave) != 3 or not clave.isdigit(): continue
                
                # Normalize Name (remove newlines and extra spaces)
                nombre_clean = " ".join(nombre.split())
                corto_clean = " ".join(corto.split()) if corto.strip() else nombre_clean[:20]
                
                # Map active status
                active = "Operación" in estatus or "Autorizada" in estatus
                
                all_institutions.append({
                    "clave": clave,
                    "nombre": nombre_clean,
                    "tipo": item['sector_name'].upper(),
                    "corto": corto_clean,
                    "active": active
                })
        
        df = pd.DataFrame(all_institutions)
        if not df.empty:
            # Sort by active first so duplicates keep the active one if any
            df = df.sort_values('active', ascending=False).drop_duplicates(subset=['clave'], keep='first')
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
        df_final = df.drop(columns=['tipo']).drop_duplicates(subset=['clave'])
        
        manager_inst = SCD2Manager(target_table="instituciones_bancarias", natural_key="clave", schema="financial")
        return manager_inst.upsert(df_final)

if __name__ == "__main__":
    processor = CasfimProcessor()
    html_path = "/home/ia/.gemini/antigravity/brain/2327746d-a199-4d1a-a45c-f26fc6209bb4/scratch/casfim_links.html"
    links = processor.get_links_from_html(html_path)
    links = processor.download_pdfs(links)
    processed = processor.process_with_docling(links)
    df = processor.extract_institutions(processed)
    logging.info(f"Extracted {len(df)} institutions.")
    processor.load_to_db(df)
