from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.scd2_manager import SCD2Manager
from app.core.auth import get_current_user
from typing import List, Optional
from sqlalchemy import text

router = APIRouter()

@router.get("/productos", tags=["Fiscal"])
async def search_productos(
    q: Optional[str] = Query(None, description="Buscar por descripción o código (Fuzzy Search GIN)"),
    current_user: dict = Depends(get_current_user)
):
    """Buscar productos y servicios del SAT con soporte de búsqueda predictiva ultrarrápida"""
    manager = SCD2Manager(target_table="cat_prod_serv", natural_key="code", schema="fiscal")
    
    if q and len(q) >= 2:
        # Usar índice trigram GIN para resolver búsquedas en menos de 50ms
        query = text("""
            SELECT id, code, description, active
            FROM fiscal.cat_prod_serv
            WHERE (description ILIKE :q OR code ILIKE :q)
              AND scd_is_current = TRUE
            ORDER BY code
            LIMIT 100
        """)
        with manager.engine.connect() as conn:
            result = conn.execute(query, {"q": f"%{q}%"})
            return [dict(row._asdict()) for row in result]
            
    return manager.search(limit=100)

@router.get("/productos/hierarchy", tags=["Fiscal"])
async def get_productos_hierarchy(
    parent_code: Optional[str] = Query(None, description="Código jerárquico padre (ej. vacio para Divisiones, 2 digitos para Grupos, 4 para Clases, 6 para Productos)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Navegación jerárquica por niveles (División -> Grupo -> Clase -> Producto)
    según el estándar del catálogo de productos y servicios del SAT (8 dígitos).
    """
    manager = SCD2Manager(target_table="cat_prod_serv", natural_key="code", schema="fiscal")
    
    if parent_code and len(parent_code) == 8:
        if parent_code.endswith('000000'):
            parent_code = parent_code[:2]
        elif parent_code.endswith('0000'):
            parent_code = parent_code[:4]
        elif parent_code.endswith('00'):
            parent_code = parent_code[:6]

    if not parent_code:
        # Nivel 1: Divisiones (ej. 10000000, 20000000)
        query = text("""
            SELECT code, description, id
            FROM fiscal.cat_prod_serv
            WHERE code LIKE '__000000'
              AND scd_is_current = TRUE
            ORDER BY code
        """)
        params = {}
    elif len(parent_code) == 2:
        # Nivel 2: Grupos (ej. 10100000, 10110000)
        query = text("""
            SELECT code, description, id
            FROM fiscal.cat_prod_serv
            WHERE code LIKE :prefix || '__0000'
              AND code != :prefix || '000000'
              AND scd_is_current = TRUE
            ORDER BY code
        """)
        params = {"prefix": parent_code}
    elif len(parent_code) == 4:
        # Nivel 3: Clases (ej. 10101500, 10101600)
        query = text("""
            SELECT code, description, id
            FROM fiscal.cat_prod_serv
            WHERE code LIKE :prefix || '__00'
              AND code != :prefix || '0000'
              AND scd_is_current = TRUE
            ORDER BY code
        """)
        params = {"prefix": parent_code}
    elif len(parent_code) == 6:
        # Nivel 4: Productos/Servicios individuales (ej. 10101501)
        query = text("""
            SELECT code, description, id
            FROM fiscal.cat_prod_serv
            WHERE code LIKE :prefix || '__'
              AND code NOT LIKE '%00'
              AND scd_is_current = TRUE
            ORDER BY code
        """)
        params = {"prefix": parent_code}
    else:
        raise HTTPException(status_code=400, detail="Formato de parent_code inválido. Debe ser de 2, 4 o 6 dígitos (o 8 dígitos con sufijos de ceros).")
        
    with manager.engine.connect() as conn:
        result = conn.execute(query, params)
        return [dict(row._asdict()) for row in result]

@router.get("/unidades-medida", tags=["Fiscal"])
async def search_unidades(
    q: Optional[str] = Query(None, description="Buscar por nombre o código de unidad (ej. H87, E48) (Fuzzy)"),
    current_user: dict = Depends(get_current_user)
):
    """Buscar unidades de medida del SAT"""
    manager = SCD2Manager(target_table="cat_unidades", natural_key="code", schema="fiscal")
    
    if q and len(q) >= 1:
        query = text("""
            SELECT id, code, name, active
            FROM fiscal.cat_unidades
            WHERE (name ILIKE :q OR code ILIKE :q)
              AND scd_is_current = TRUE
            ORDER BY code
            LIMIT 100
        """)
        with manager.engine.connect() as conn:
            result = conn.execute(query, {"q": f"%{q}%"})
            return [dict(row._asdict()) for row in result]
            
    return manager.search(limit=100)

@router.get("/formas-pago", tags=["Fiscal"])
async def get_formas_pago(current_user: dict = Depends(get_current_user)):
    """Listar formas de pago"""
    manager = SCD2Manager(target_table="cat_forma_pago", natural_key="code", schema="fiscal")
    return manager.search(limit=100)

@router.get("/metodos-pago", tags=["Fiscal"])
async def get_metodos_pago(current_user: dict = Depends(get_current_user)):
    """Listar métodos de pago"""
    manager = SCD2Manager(target_table="cat_metodo_pago", natural_key="code", schema="fiscal")
    return manager.search(limit=100)

@router.get("/monedas", tags=["Fiscal"])
async def get_monedas(current_user: dict = Depends(get_current_user)):
    """Listar monedas oficiales"""
    manager = SCD2Manager(target_table="cat_monedas", natural_key="code", schema="fiscal")
    return manager.search(limit=100)

@router.get("/exportacion", tags=["Fiscal"])
async def get_exportacion(current_user: dict = Depends(get_current_user)):
    """Listar tipos de exportación"""
    manager = SCD2Manager(target_table="cat_exportacion", natural_key="code", schema="fiscal")
    return manager.search(limit=100)

@router.get("/objeto-impuesto", tags=["Fiscal"])
async def get_objeto_impuesto(current_user: dict = Depends(get_current_user)):
    """Listar tipos de objeto de impuesto"""
    manager = SCD2Manager(target_table="cat_objeto_imp", natural_key="code", schema="fiscal")
    return manager.search(limit=100)
