from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.scd2_manager import SCD2Manager
from app.core.auth import get_current_user
from typing import List, Optional
from sqlalchemy import text

router = APIRouter()

@router.get("/instituciones", tags=["Finanzas"])
async def get_instituciones(
    nombre: Optional[str] = Query(None, description="Buscar por nombre o clave de la institución"),
    tipo_id: Optional[str] = Query(None, description="Filtrar por UUID del tipo de entidad (Sector)"),
    solo_activas: bool = Query(True, description="Filtrar solo entidades activas y operativas"),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar o buscar instituciones financieras (CASFIM).
    Soporta filtros combinados por sector, búsquedas por nombre, y alternancia entre 
    histórico completo o solo entidades activas. Retorna información de fusión y sucesores.
    """
    manager = SCD2Manager(target_table="instituciones_bancarias", natural_key=["clave", "tipo_entidad_id"], schema="financial")
    
    query = """
        SELECT 
            f.id,
            f.clave,
            f.nombre,
            f.corto,
            f.estatus,
            f.active,
            t.id as tipo_entidad_id,
            t.nombre as tipo_entidad,
            f.sucesora_id,
            s.nombre as sucesora_nombre
        FROM financial.instituciones_bancarias f
        LEFT JOIN financial.cat_entidad_tipos t ON f.tipo_entidad_id = t.id
        LEFT JOIN financial.instituciones_bancarias s ON f.sucesora_id = s.id AND s.scd_is_current = TRUE
        WHERE f.scd_is_current = TRUE
    """
    params = {}
    
    if nombre:
        query += " AND (f.nombre ILIKE :nombre OR f.corto ILIKE :nombre OR f.clave ILIKE :nombre)"
        params["nombre"] = f"%{nombre}%"
        
    if tipo_id:
        query += " AND f.tipo_entidad_id = CAST(:tipo_id AS uuid)"
        params["tipo_id"] = tipo_id
        
    if solo_activas:
        query += " AND f.estatus = 'ACTIVA' AND f.active = TRUE"
        
    query += " ORDER BY f.nombre"
    
    with manager.engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(r._mapping) for r in result]

@router.get("/tipos-entidad", tags=["Finanzas"])
async def get_tipos_entidad(current_user: dict = Depends(get_current_user)):
    """Obtener tipos de entidad (Sectores) disponibles para filtrado en frontend"""
    manager = SCD2Manager(target_table="cat_entidad_tipos", natural_key="nombre", schema="financial")
    with manager.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, nombre 
            FROM financial.cat_entidad_tipos 
            WHERE scd_is_current = TRUE 
            ORDER BY nombre
        """))
        return [dict(row._mapping) for row in result]
