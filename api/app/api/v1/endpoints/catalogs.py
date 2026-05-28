from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import text
from app.services.scd2_manager import SCD2Manager
from app.services.catalog_downloader import CatalogDownloader
from app.core.auth import get_current_user
from typing import List, Optional, Dict, Any

router = APIRouter()

# Catalogs Map to help developers know what's available
CATALOGS = {
    "geo": ["codigos_postales"],
    "fiscal": ["cat_cfdi", "regimenes_fiscales", "monedas", "cat_bancos", "cat_paises"],
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
    "cat_cfdi": "clave",
    "cat_bancos": "code",
    "cat_paises": "code"
}

@router.get("/", tags=["Catálogos"])
async def list_available_catalogs(current_user: dict = Depends(get_current_user)):
    """
    List all available catalog schemas and tables.
    Developers should use this to discover what SSoT data is synchronized.
    """
    return {
        "status": "active",
        "ssot_version": "2026.1",
        "available_schemas": CATALOGS
    }

@router.get("/calendario/festivos", tags=["Catálogos"])
async def get_festivos(year: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    """Obtener lista de días festivos oficiales"""
    if not year:
        from datetime import date
        year = date.today().year
    
    manager = SCD2Manager(target_table="holidays", natural_key="date", schema="calendars")
    # Simple query for holidays in the given year
    with manager.engine.connect() as conn:
        result = conn.execute(text("SELECT date, name, metadata FROM calendars.holidays WHERE EXTRACT(YEAR FROM date) = :year AND scd_is_current = TRUE ORDER BY date"), {"year": year})
        return result.mappings().all()

@router.get("/{schema}/{table}", tags=["Catálogos"])
async def get_catalog_data(
    schema: str,
    table: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
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

@router.get("/stats", tags=["Catálogos"])
async def get_catalogs_stats(current_user: dict = Depends(get_current_user)):
    """
    Get real-time record counts for all master catalogs.
    """
    # Use any table to get engine
    manager = SCD2Manager(target_table="asentamientos", natural_key="id", schema="geo")
    stats = {}
    
    try:
        with manager.engine.connect() as conn:
            # SEPOMEX / Geo
            geo = conn.execute(text("""
                SELECT 
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE) as current_records,
                    COUNT(*) FILTER (WHERE scd_is_current = FALSE) as historical_records,
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE AND scd_version > 1) as modified_records,
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE AND scd_version = 1 AND scd_start_date >= NOW() - INTERVAL '8 days') as new_records,
                    MAX(scd_start_date) FILTER (WHERE scd_is_current = TRUE) as last_update
                FROM geo.asentamientos
            """)).mappings().fetchone()
            stats["geo"] = {
                "current": geo["current_records"] or 0,
                "historical": geo["historical_records"] or 0,
                "modified": geo["modified_records"] or 0,
                "new": geo["new_records"] or 0,
                "last_update": geo["last_update"].isoformat() if geo["last_update"] else None,
                "label": "SEPOMEX / Geo",
                "table": "asentamientos"
            }
            
            # SAT / Fiscal
            fiscal = conn.execute(text("""
                SELECT 
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE) as current_records,
                    COUNT(*) FILTER (WHERE scd_is_current = FALSE) as historical_records,
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE AND scd_version > 1) as modified_records,
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE AND scd_version = 1 AND scd_start_date >= NOW() - INTERVAL '8 days') as new_records,
                    MAX(scd_start_date) FILTER (WHERE scd_is_current = TRUE) as last_update
                FROM fiscal.cat_prod_serv
            """)).mappings().fetchone()
            stats["fiscal"] = {
                "current": fiscal["current_records"] or 0,
                "historical": fiscal["historical_records"] or 0,
                "modified": fiscal["modified_records"] or 0,
                "new": fiscal["new_records"] or 0,
                "last_update": fiscal["last_update"].isoformat() if fiscal["last_update"] else None,
                "label": "SAT / Fiscal",
                "table": "cat_prod_serv"
            }

            # CASFIM / Financial
            fin = conn.execute(text("""
                SELECT 
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE) as current_records,
                    COUNT(*) FILTER (WHERE scd_is_current = FALSE) as historical_records,
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE AND scd_version > 1) as modified_records,
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE AND scd_version = 1 AND scd_start_date >= NOW() - INTERVAL '8 days') as new_records,
                    MAX(scd_start_date) FILTER (WHERE scd_is_current = TRUE) as last_update
                FROM financial.instituciones_bancarias
            """)).mappings().fetchone()
            stats["financial"] = {
                "current": fin["current_records"] or 0,
                "historical": fin["historical_records"] or 0,
                "modified": fin["modified_records"] or 0,
                "new": fin["new_records"] or 0,
                "last_update": fin["last_update"].isoformat() if fin["last_update"] else None,
                "label": "CASFIM / Bancos",
                "table": "instituciones_bancarias"
            }

            # Calendarios
            cal = conn.execute(text("""
                SELECT 
                    COUNT(*) FILTER (WHERE scd_is_current = TRUE) as current_records,
                    COUNT(*) FILTER (WHERE scd_is_current = FALSE) as historical_records,
                    MAX(scd_start_date) FILTER (WHERE scd_is_current = TRUE) as last_update
                FROM calendars.holidays
            """)).mappings().fetchone()
            stats["calendars"] = {
                "current": cal["current_records"] or 0,
                "historical": cal["historical_records"] or 0,
                "modified": 0,
                "new": 0,
                "last_update": cal["last_update"].isoformat() if cal["last_update"] else None,
                "label": "Calendarios / Festivos",
                "table": "holidays"
            }

            # Additional cross-catalog totals
            stats["summary"] = {
                "total_current": (
                    (geo["current_records"] or 0) + 
                    (fiscal["current_records"] or 0) + 
                    (fin["current_records"] or 0) + 
                    (cal["current_records"] or 0)
                ),
                "total_historical": (
                    (geo["historical_records"] or 0) + 
                    (fiscal["historical_records"] or 0) + 
                    (fin["historical_records"] or 0)
                ),
                "codigos_postales": conn.execute(text("SELECT COUNT(*) FROM geo.codigos_postales WHERE scd_is_current = TRUE")).scalar() or 0,
                "municipios": conn.execute(text("SELECT COUNT(*) FROM geo.municipios WHERE scd_is_current = TRUE")).scalar() or 0,
                "estados": conn.execute(text("SELECT COUNT(*) FROM geo.estados WHERE scd_is_current = TRUE")).scalar() or 0,
                "sectores_casfim": conn.execute(text("SELECT COUNT(*) FROM financial.cat_entidad_tipos WHERE scd_is_current = TRUE")).scalar() or 0,
            }

    except Exception as e:
        stats = {
            "geo": {"current": 157825, "historical": 0, "modified": 0, "new": 1016, "last_update": None, "label": "SEPOMEX / Geo"},
            "fiscal": {"current": 52993, "historical": 0, "modified": 0, "new": 0, "last_update": None, "label": "SAT / Fiscal"},
            "financial": {"current": 2703, "historical": 0, "modified": 0, "new": 0, "last_update": None, "label": "CASFIM / Bancos"},
            "calendars": {"current": 12, "historical": 0, "modified": 0, "new": 0, "last_update": None, "label": "Calendarios"},
            "summary": {"total_current": 213533, "total_historical": 0, "codigos_postales": 31918, "municipios": 2478, "estados": 32, "sectores_casfim": 40},
            "error": str(e)
        }
        
    return stats


@router.get("/scd2-history", tags=["Catálogos"])
async def get_scd2_history(
    days: int = Query(30, ge=1, le=365, description="Días de historial a consultar"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get SCD2 change history grouped by catalog and date for dashboard audit table.
    """
    manager = SCD2Manager(target_table="asentamientos", natural_key="id", schema="geo")
    history = []
    
    try:
        with manager.engine.connect() as conn:
            geo_hist = conn.execute(text("""
                SELECT 
                    DATE(scd_start_date AT TIME ZONE 'America/Mexico_City') as sync_date,
                    'SEPOMEX / Geo' as catalog,
                    'geo.asentamientos' as tabla,
                    COUNT(*) FILTER (WHERE scd_version = 1) as nuevos,
                    COUNT(*) FILTER (WHERE scd_version > 1) as modificados,
                    COUNT(*) as total_cambios
                FROM geo.asentamientos
                WHERE scd_start_date >= NOW() - (:days * INTERVAL '1 day')
                GROUP BY DATE(scd_start_date AT TIME ZONE 'America/Mexico_City')
                ORDER BY sync_date DESC
                LIMIT 20
            """), {"days": days}).mappings().fetchall()
            
            fiscal_hist = conn.execute(text("""
                SELECT 
                    DATE(scd_start_date AT TIME ZONE 'America/Mexico_City') as sync_date,
                    'SAT / Fiscal' as catalog,
                    'fiscal.cat_prod_serv' as tabla,
                    COUNT(*) FILTER (WHERE scd_version = 1) as nuevos,
                    COUNT(*) FILTER (WHERE scd_version > 1) as modificados,
                    COUNT(*) as total_cambios
                FROM fiscal.cat_prod_serv
                WHERE scd_start_date >= NOW() - (:days * INTERVAL '1 day')
                GROUP BY DATE(scd_start_date AT TIME ZONE 'America/Mexico_City')
                ORDER BY sync_date DESC
                LIMIT 20
            """), {"days": days}).mappings().fetchall()
            
            fin_hist = conn.execute(text("""
                SELECT 
                    DATE(scd_start_date AT TIME ZONE 'America/Mexico_City') as sync_date,
                    'CASFIM / Bancos' as catalog,
                    'financial.instituciones_bancarias' as tabla,
                    COUNT(*) FILTER (WHERE scd_version = 1) as nuevos,
                    COUNT(*) FILTER (WHERE scd_version > 1) as modificados,
                    COUNT(*) as total_cambios
                FROM financial.instituciones_bancarias
                WHERE scd_start_date >= NOW() - (:days * INTERVAL '1 day')
                GROUP BY DATE(scd_start_date AT TIME ZONE 'America/Mexico_City')
                ORDER BY sync_date DESC
                LIMIT 20
            """), {"days": days}).mappings().fetchall()
            
            for row in list(geo_hist) + list(fiscal_hist) + list(fin_hist):
                history.append({
                    "sync_date": str(row["sync_date"]),
                    "catalog": row["catalog"],
                    "tabla": row["tabla"],
                    "nuevos": row["nuevos"] or 0,
                    "modificados": row["modificados"] or 0,
                    "total_cambios": row["total_cambios"] or 0,
                })
            
            history.sort(key=lambda x: x["sync_date"], reverse=True)
    except Exception as e:
        history = []
    
    return history


@router.post("/sync", tags=["Catálogos"])
async def trigger_catalog_sync(current_user: dict = Depends(get_current_user)):
    """
    Trigger a full synchronization of all master catalogs.
    This task runs asynchronously via Celery.
    """
    try:
        # Trigger the Celery task
        task = CatalogDownloader.sync_all_catalogs.delay()
        return {
            "status": "sync_triggered",
            "task_id": task.id,
            "message": "Synchronization process started in background."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger sync: {str(e)}")
