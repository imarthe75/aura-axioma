from fastapi import APIRouter, Query, HTTPException
from app.services.scd2_manager import SCD2Manager
from typing import List, Optional
from sqlalchemy import text

router = APIRouter()

@router.get("/codigo-postal/{cp}", tags=["Geografía"])
async def obtener_detalles_cp(cp: str):
    """
    Obtener detalles de un Código Postal (CP) en cascada:
    Devuelve asentamientos, municipio, estado y país asociados.
    """
    manager = SCD2Manager(target_table="codigos_postales", natural_key="cp", schema="geo")
    
    query = text("""
        SELECT 
            codigo_postal,
            asentamiento,
            tipo_asentamiento,
            zona,
            municipio,
            estado,
            pais,
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
        "codigo_postal": first["codigo_postal"],
        "pais": first["pais"],
        "codigo_telefonico": first["codigo_telefonico"],
        "estado": first["estado"],
        "municipio": first["municipio"],
        "asentamientos": [
            {
                "nombre": r["asentamiento"], 
                "tipo": r["tipo_asentamiento"],
                "zona": r["zona"]
            } 
            for r in rows
        ]
    }

@router.get("/paises", tags=["Geografía"])
async def obtener_paises(q: Optional[str] = None):
    """Listar o buscar Países (Catálogo Global)"""
    manager = SCD2Manager(target_table="paises", natural_key="iso_alpha3", schema="geo")
    return manager.search(search_term=q, limit=250)

@router.get("/estados", tags=["Geografía"])
async def obtener_estados(q: Optional[str] = None):
    """Listar o buscar Estados de México"""
    manager = SCD2Manager(target_table="estados", natural_key="state_code", schema="geo")
    return manager.search(search_term=q, limit=50)

@router.get("/municipios", tags=["Geografía"])
async def obtener_municipios(estado: Optional[str] = None, q: Optional[str] = None):
    """Listar Municipios filtrados por estado o nombre"""
    manager = SCD2Manager(target_table="municipios", natural_key="municipality_code", schema="geo")
    filters = {}
    if estado:
        filters["state_id"] = estado
    return manager.search(search_term=q, limit=100, **filters)

@router.get("/asentamientos", tags=["Geografía"])
async def buscar_asentamientos(q: str = Query(..., min_length=3, description="Nombre de colonia o CP")):
    """Buscar Asentamientos (Colonias) por nombre o Código Postal"""
    manager = SCD2Manager(target_table="asentamientos", natural_key="id", schema="geo")
    
    query = text("""
        SELECT *
        FROM geo.vw_geografia_mexico
        WHERE asentamiento ILIKE :q OR codigo_postal ILIKE :q
        LIMIT 50
    """)
    
    with manager.engine.connect() as conn:
        result = conn.execute(query, {"q": f"%{q}%"})
        return [dict(row._asdict()) for row in result]
