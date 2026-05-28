from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.scd2_manager import SCD2Manager
from app.core.auth import get_current_user
from typing import List, Optional
from sqlalchemy import text

router = APIRouter()

@router.get("/paises", tags=["Geografía"])
async def obtener_paises(q: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Listar o buscar Países (Catálogo Global)"""
    manager = SCD2Manager(target_table="paises", natural_key="iso_alpha3", schema="geo")
    return manager.search(search_term=q, limit=250)

@router.get("/estados", tags=["Geografía"])
async def obtener_estados(
    pais_id: Optional[str] = Query(None, description="Filtrar por UUID del país sucesor"),
    q: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Listar Estados de México, opcionalmente filtrados por país"""
    manager = SCD2Manager(target_table="estados", natural_key="state_code", schema="geo")
    filters = {}
    if pais_id:
        filters["country_id"] = pais_id
    return manager.search(search_term=q, limit=50, **filters)

@router.get("/municipios", tags=["Geografía"])
async def obtener_municipios(
    estado_id: Optional[str] = Query(None, description="Filtrar por UUID del estado"),
    q: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Listar Municipios filtrados por estado o nombre"""
    manager = SCD2Manager(target_table="municipios", natural_key="municipality_code", schema="geo")
    filters = {}
    if estado_id:
        filters["state_id"] = estado_id
    res = manager.search(search_term=q, limit=100, **filters)
    return sorted(res, key=lambda x: x.get("name", ""))

@router.get("/codigos-postales", tags=["Geografía"])
async def obtener_codigos_postales(
    municipio_id: str = Query(..., description="UUID del municipio"),
    current_user: dict = Depends(get_current_user)
):
    """Obtener códigos postales únicos asociados a un municipio"""
    manager = SCD2Manager(target_table="codigos_postales", natural_key="cp", schema="geo")
    query = text("""
        SELECT DISTINCT cp.id, cp.cp
        FROM geo.asentamientos a
        JOIN geo.codigos_postales cp ON a.cp_id = cp.id
        WHERE a.municipality_id = CAST(:municipio_id AS uuid)
          AND a.scd_is_current = TRUE
        ORDER BY cp.cp
    """)
    with manager.engine.connect() as conn:
        result = conn.execute(query, {"municipio_id": municipio_id})
        return [dict(row._asdict()) for row in result]

@router.get("/asentamientos", tags=["Geografía"])
async def obtener_asentamientos(
    municipio_id: Optional[str] = Query(None, description="Filtrar por UUID del municipio"),
    cp_id: Optional[str] = Query(None, description="Filtrar por UUID del Código Postal"),
    q: Optional[str] = Query(None, description="Término para búsqueda predictiva Fuzzy (trigram)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar o buscar Asentamientos (Colonias) en cascada o de forma predictiva global.
    Si se provee 'q', ejecuta una búsqueda Fuzzy acelerada por el índice pg_trgm en Postgres.
    """
    manager = SCD2Manager(target_table="asentamientos", natural_key="id", schema="geo")
    
    if q and len(q) >= 2:
        # Búsqueda predictiva Fuzzy (Trigram) global en la vista georelacional
        # pg_trgm acelera automáticamente las comparaciones ILIKE '%term%' en Postgres 18
        query = text("""
            SELECT 
                asentamiento_id as id,
                codigo_postal as cp,
                asentamiento as nombre,
                tipo_asentamiento as tipo,
                zona,
                municipio,
                municipio_id,
                estado,
                estado_id,
                pais,
                pais_id
            FROM geo.vw_geografia_mexico
            WHERE asentamiento ILIKE :q OR codigo_postal ILIKE :q
            LIMIT 50
        """)
        with manager.engine.connect() as conn:
            result = conn.execute(query, {"q": f"%{q}%"})
            return [dict(row._asdict()) for row in result]
            
    # De lo contrario, filtrado normal por municipio (cascada)
    query = text("""
        SELECT 
            a.id,
            a.name as nombre,
            at.name as tipo,
            zt.name as zona,
            cp.cp as codigo_postal
        FROM geo.asentamientos a
        JOIN geo.asentamiento_tipos at ON a.asentamiento_tipo_id = at.id
        JOIN geo.zona_tipos zt ON a.zona_tipo_id = zt.id
        JOIN geo.codigos_postales cp ON a.cp_id = cp.id
        WHERE a.scd_is_current = TRUE
          AND (CAST(:municipio_id AS uuid) IS NULL OR a.municipality_id = CAST(:municipio_id AS uuid))
          AND (CAST(:cp_id AS uuid) IS NULL OR a.cp_id = CAST(:cp_id AS uuid))
        ORDER BY a.name
        LIMIT 100
    """)
    with manager.engine.connect() as conn:
        result = conn.execute(query, {"municipio_id": municipio_id, "cp_id": cp_id})
        return [dict(row._asdict()) for row in result]

@router.get("/codigo-postal/{cp}", tags=["Geografía"])
async def obtener_detalles_cp(cp: str, current_user: dict = Depends(get_current_user)):
    """
    Búsqueda Inversa por Código Postal (CP).
    Devuelve los detalles de ubicación común (País, Estado, Municipio) y una lista 
    dinámica de asentamientos asociados a ese CP para selección en frontend.
    """
    manager = SCD2Manager(target_table="codigos_postales", natural_key="cp", schema="geo")
    
    query = text("""
        SELECT 
            asentamiento_id as id,
            codigo_postal as cp,
            asentamiento as nombre,
            tipo_asentamiento as tipo,
            zona,
            municipio,
            municipio_id,
            estado,
            estado_id,
            pais,
            pais_id,
            codigo_telefonico
        FROM geo.vw_geografia_mexico
        WHERE codigo_postal = :cp
    """)
    
    with manager.engine.connect() as conn:
        result = conn.execute(query, {"cp": cp})
        rows = [dict(row._asdict()) for row in result]
        
    if not rows:
        raise HTTPException(status_code=404, detail="Código Postal no encontrado")
        
    first = rows[0]
    return {
        "codigo_postal": first["cp"],
        "pais": first["pais"],
        "pais_id": first["pais_id"],
        "codigo_telefonico": first["codigo_telefonico"],
        "estado": first["estado"],
        "estado_id": first["estado_id"],
        "municipio": first["municipio"],
        "municipio_id": first["municipio_id"],
        "asentamientos": [
            {
                "id": r["id"], 
                "nombre": r["nombre"], 
                "tipo": r["tipo"],
                "zona": r["zona"]
            } 
            for r in rows
        ]
    }
