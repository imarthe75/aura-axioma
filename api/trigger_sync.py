from app.services.catalog_downloader import CatalogDownloader
import logging

logging.basicConfig(level=logging.INFO)
print("Triggering manual catalog sync...")
result = CatalogDownloader.sync_all_catalogs()
print(f"Result: {result}")
