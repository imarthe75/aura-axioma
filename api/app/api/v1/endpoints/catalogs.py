from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.scd2_manager import SCD2Manager
from typing import List, Optional, Dict, Any

router = APIRouter()

# Catalogs Map to help developers know what's available
CATALOGS = {
    "geo": ["codigos_postales"],
    "fiscal": ["cat_cfdi", "regimenes_fiscales", "monedas"],
    "financial": ["instituciones_bancarias"],
    "calendars": ["holidays"]
}

# Mapping of natural keys for each table to enable SCD2 searching
NATURAL_KEYS = {
    "codigos_postales": "cp",
    "holidays": "date",
    "instituciones_bancarias": "clave",
    "regimenes_fiscales": "clave",
    "monedas": "clave",
    "cat_cfdi": "clave"
}

@router.get("/", tags=["Catalogs"])
async def list_available_catalogs():
    """
    List all available catalog schemas and tables.
    Developers should use this to discover what SSoT data is synchronized.
    """
    return {
        "status": "active",
        "ssot_version": "2026.1",
        "available_schemas": CATALOGS
    }

@router.get("/{schema}/{table}", tags=["Catalogs"])
async def get_catalog_data(
    schema: str, 
    table: str, 
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    search: Optional[str] = None
):
    """
    Query current records from a specific catalog table.
    - **schema**: geo, fiscal, financial, calendars
    - **table**: table name (e.g., codigos_postales)
    - **search**: keyword to filter results (searches by natural key)
    """
    if schema not in CATALOGS or table not in CATALOGS[schema]:
        raise HTTPException(
            status_code=404, 
            detail=f"Catalog '{table}' in schema '{schema}' not found. Check /catalogs/ for available options."
        )
    
    nk = NATURAL_KEYS.get(table, "id")
    
    manager = SCD2Manager(target_table=table, natural_key=nk, schema=schema)
    
    try:
        # Note: In a production environment, SCD2Manager.search should support offset/limit
        # For this version, we use the limit parameter
        results = manager.search(search_term=search, limit=page_size)
        
        return {
            "schema": schema,
            "table": table,
            "params": {
                "natural_key": nk,
                "limit": page_size,
                "search": search
            },
            "count": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
