from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.scd2_manager import SCD2Manager
from app.core.auth import get_current_user
from typing import List, Optional
from sqlalchemy import text

router = APIRouter()

@router.get("/localidades", tags=["INEGI"])
async def obtener_localidades(
    municipio_id: Optional[str] = Query(None, description="UUID del municipio (Spanish)"),
    municipality_id: Optional[str] = Query(None, description="UUID del municipio (English)"),
    q: Optional[str] = Query(None, description="Nombre de la localidad"),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar localidades de INEGI.
    Proporciona datos estadísticos y geográficos de alta precisión.
    """
    manager = SCD2Manager(target_table="localidades", natural_key="clave_localidad", schema="inegi")
    
    m_id = municipio_id or municipality_id
    filters = {}
    if m_id:
        filters["municipality_id"] = m_id
        
    return manager.search(search_term=q, limit=100, **filters)

@router.get("/georeferencia", tags=["INEGI"])
async def obtener_georeferencia(lat: float, lon: float, radio_km: float = 1.0, current_user: dict = Depends(get_current_user)):
    """
    Buscar la localidad de INEGI más cercana por coordenadas.
    """
    manager = SCD2Manager(target_table="localidades", natural_key="clave_localidad", schema="inegi")
    
    query = text("""
        SELECT 
            l.*,
            m.name as municipio,
            e.name as estado
        FROM inegi.localidades l
        JOIN geo.municipios m ON l.municipality_id = m.id
        JOIN geo.estados e ON m.state_id = e.id
        WHERE l.scd_is_current = TRUE
        ORDER BY ((l.longitud - :lon) * (l.longitud - :lon) + (l.latitud - :lat) * (l.latitud - :lat)) ASC
        LIMIT 5
    """)
    
    with manager.engine.connect() as conn:
        result = conn.execute(query, {"lat": lat, "lon": lon})
        return [dict(row._asdict()) for row in result]
