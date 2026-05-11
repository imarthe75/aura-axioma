from fastapi import APIRouter, Query, HTTPException
from app.services.scd2_manager import SCD2Manager
from typing import List, Optional
from sqlalchemy import text

router = APIRouter()

@router.get("/instituciones", tags=["Financial"])
async def get_instituciones(
    q: Optional[str] = None, 
    tipo: Optional[str] = Query(None, description="Filter by Entity Type (e.g. BANCA MULTIPLE, SOFIPO)")
):
    """List or search financial institutions (CASFIM)"""
    manager = SCD2Manager(target_table="instituciones_bancarias", natural_key="clave", schema="financial")
    filters = {}
    if tipo:
        filters["tipo_entidad"] = tipo
    return manager.search(search_term=q, limit=100, **filters)

@router.get("/tipos", tags=["Financial"])
async def get_tipos_entidad():
    """Get unique entity types for filtering"""
    manager = SCD2Manager(target_table="instituciones_bancarias", natural_key="clave", schema="financial")
    with manager.engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT tipo_entidad FROM financial.instituciones_bancarias WHERE scd_is_current = TRUE AND tipo_entidad IS NOT NULL"))
        return [row[0] for row in result]
