from fastapi import APIRouter, Query, HTTPException
from app.services.scd2_manager import SCD2Manager
from typing import List, Optional
from sqlalchemy import text

router = APIRouter()

@router.get("/instituciones", tags=["Finanzas"])
async def get_instituciones(
    nombre: Optional[str] = Query(None, description="Buscar por nombre de la institución"), 
    tipo: Optional[str] = Query(None, description="Filtrar por nombre del tipo de entidad (ej. BANCA MULTIPLE, SOFIPO)")
):
    """Listar o buscar instituciones financieras (CASFIM)"""
    manager = SCD2Manager(target_table="instituciones_bancarias", natural_key="clave", schema="financial")
    
    query = """
        SELECT f.clave, f.nombre, f.corto, t.nombre as tipo_entidad
        FROM financial.instituciones_bancarias f
        LEFT JOIN financial.cat_entidad_tipos t ON f.tipo_entidad_id = t.id
        WHERE f.scd_is_current = TRUE
    """
    params = {}
    
    if nombre:
        query += " AND f.nombre ILIKE :nombre"
        params["nombre"] = f"%{nombre}%"
    
    if tipo:
        query += " AND t.nombre = :tipo"
        params["tipo"] = tipo
        
    with manager.engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(r._mapping) for r in result]

@router.get("/tipos-entidad", tags=["Finanzas"])
async def get_tipos_entidad():
    """Obtener tipos de entidad disponibles para filtrado"""
    manager = SCD2Manager(target_table="cat_entidad_tipos", natural_key="nombre", schema="financial")
    with manager.engine.connect() as conn:
        result = conn.execute(text("SELECT nombre FROM financial.cat_entidad_tipos WHERE scd_is_current = TRUE"))
        return [row[0] for row in result]
