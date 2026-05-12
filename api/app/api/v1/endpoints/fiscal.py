from fastapi import APIRouter, Query, HTTPException
from app.services.scd2_manager import SCD2Manager
from typing import List, Optional
from sqlalchemy import text

router = APIRouter()

@router.get("/productos-servicios", tags=["Fiscal"])
async def search_productos(
    q: Optional[str] = Query(None, description="Buscar por descripción o código"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría (primeros 2 dígitos del código)")
):
    """Buscar productos y servicios del SAT"""
    manager = SCD2Manager(target_table="cat_prod_serv", natural_key="code", schema="fiscal")
    filters = {}
    if categoria:
        # Note: Ideally we add a filter for the prefix of 'code'
        pass
    
    return manager.search(search_term=q, limit=100, **filters)

@router.get("/unidades-medida", tags=["Fiscal"])
async def search_unidades(
    q: Optional[str] = Query(None, description="Buscar por nombre o código de unidad (ej. H87, E48)")
):
    """Buscar unidades de medida del SAT"""
    manager = SCD2Manager(target_table="cat_unidades", natural_key="code", schema="fiscal")
    return manager.search(search_term=q, limit=100)

@router.get("/formas-pago", tags=["Fiscal"])
async def get_formas_pago():
    """Listar formas de pago (ej. Efectivo, Transferencia)"""
    manager = SCD2Manager(target_table="cat_forma_pago", natural_key="code", schema="fiscal")
    return manager.search(limit=100)

@router.get("/metodos-pago", tags=["Fiscal"])
async def get_metodos_pago():
    """Listar métodos de pago (ej. PUE, PPD)"""
    manager = SCD2Manager(target_table="cat_metodo_pago", natural_key="code", schema="fiscal")
    return manager.search(limit=100)

@router.get("/monedas", tags=["Fiscal"])
async def get_monedas():
    """Listar monedas oficiales (ej. MXN, USD)"""
    manager = SCD2Manager(target_table="cat_monedas", natural_key="code", schema="fiscal")
    return manager.search(limit=100)

@router.get("/exportacion", tags=["Fiscal"])
async def get_exportacion():
    """Listar tipos de exportación"""
    manager = SCD2Manager(target_table="cat_exportacion", natural_key="code", schema="fiscal")
    return manager.search(limit=100)

@router.get("/objeto-impuesto", tags=["Fiscal"])
async def get_objeto_impuesto():
    """Listar tipos de objeto de impuesto"""
    manager = SCD2Manager(target_table="cat_objeto_imp", natural_key="code", schema="fiscal")
    return manager.search(limit=100)

@router.get("/categorias", tags=["Fiscal"])
async def get_sat_categories():
    """Get common SAT product categories (Divisions)"""
    # This could be a separate table or derived from cat_prod_serv
    # For now, let's return a standard list of SAT Divisions
    return [
        {"id": "10", "name": "Material Vivo Vegetal y Animal"},
        {"id": "11", "name": "Material de Minerales, Metalurgia y Secciones"},
        {"id": "12", "name": "Material Químico"},
        {"id": "13", "name": "Resina, Elastómeros y Herramientas"},
        {"id": "14", "name": "Materiales de Papel"},
        {"id": "15", "name": "Combustibles y Lubricantes"},
        {"id": "20", "name": "Maquinaria de Minería y Perforación"},
        {"id": "21", "name": "Maquinaria de Agricultura y Silvicultura"},
        {"id": "22", "name": "Maquinaria de Construcción y Edificación"},
        {"id": "23", "name": "Maquinaria de Fabricación"},
        {"id": "24", "name": "Maquinaria de Embalaje"},
        {"id": "25", "name": "Maquinaria de Servicio"},
        {"id": "26", "name": "Maquinaria de Energía y Generación"},
        {"id": "27", "name": "Maquinaria de Telecomunicaciones"},
        {"id": "30", "name": "Componentes y Suministros de Fabricación"},
        {"id": "31", "name": "Componentes de Fabricación"},
        {"id": "32", "name": "Componentes de Construcción"},
        {"id": "39", "name": "Componentes Eléctricos"},
        {"id": "40", "name": "Sistemas de Calefacción y Ventilación"},
        {"id": "41", "name": "Equipo de Laboratorio"},
        {"id": "42", "name": "Equipo Médico"},
        {"id": "43", "name": "Equipo de Información y Computación"},
        {"id": "44", "name": "Equipo de Oficina"},
        {"id": "45", "name": "Equipo de Impresión y Copiado"},
        {"id": "46", "name": "Equipo de Defensa y Seguridad"},
        {"id": "47", "name": "Equipo de Limpieza"},
        {"id": "48", "name": "Equipo de Almacenamiento"},
        {"id": "49", "name": "Equipo de Entretenimiento"},
        {"id": "50", "name": "Alimentos, Bebidas y Tabaco"},
        {"id": "51", "name": "Medicamentos y Productos Farmacéuticos"},
        {"id": "52", "name": "Artículos de Limpieza y de Hogar"},
        {"id": "53", "name": "Ropa, Calzado y Equipaje"},
        {"id": "54", "name": "Relojes, Joyería y Artículos de Regalo"},
        {"id": "55", "name": "Publicaciones Impresas y Multimedia"},
        {"id": "56", "name": "Muebles y Mobiliario"},
        {"id": "60", "name": "Instrumentos Musicales y Juguetes"},
        {"id": "70", "name": "Servicios de Limpieza y Manejo de Desechos"},
        {"id": "71", "name": "Servicios de Consultoría"},
        {"id": "72", "name": "Servicios de Edificación y Construcción"},
        {"id": "73", "name": "Servicios de Fabricación Industrial"},
        {"id": "76", "name": "Servicios de Ingeniería y Otros"},
        {"id": "77", "name": "Servicios de Medio Ambiente"},
        {"id": "78", "name": "Servicios de Transporte y Logística"},
        {"id": "80", "name": "Servicios de Negocios"},
        {"id": "81", "name": "Servicios Financieros y de Seguros"},
        {"id": "82", "name": "Servicios de Educación y Capacitación"},
        {"id": "83", "name": "Servicios Públicos y de Gobierno"},
        {"id": "84", "name": "Servicios de Salud"},
        {"id": "85", "name": "Servicios de Entretenimiento"},
        {"id": "86", "name": "Servicios de Hotelería y Restauración"},
        {"id": "90", "name": "Servicios de Viajes y Turismo"},
        {"id": "91", "name": "Servicios de Asociaciones y Organizaciones"},
        {"id": "92", "name": "Servicios de Defensa Nacional y Seguridad"},
        {"id": "93", "name": "Servicios de Administración Pública"},
        {"id": "94", "name": "Servicios de Organizaciones No Gubernamentales"},
        {"id": "95", "name": "Servicios de Tierra e Infraestructura"}
    ]
