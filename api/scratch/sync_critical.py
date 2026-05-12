import pandas as pd
import logging
from sqlalchemy import text
from app.services.scd2_manager import SCD2Manager
from app.services.catalog_downloader import CatalogDownloader

logging.basicConfig(level=logging.INFO)

def sync_critical_only():
    print("Syncing Financial and Fiscal catalogs only...")
    CatalogDownloader.sync_casfim()
    CatalogDownloader.sync_sat_catalogs()
    print("Sync complete.")

if __name__ == "__main__":
    sync_critical_only()
