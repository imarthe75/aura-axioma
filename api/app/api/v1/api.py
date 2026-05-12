from fastapi import APIRouter
from app.api.v1.endpoints import geo, catalogs, financial, fiscal, inegi

api_router = APIRouter()

# English Prefixes (for backward compatibility)
api_router.include_router(geo.router, prefix="/geo", tags=["Geo"])
api_router.include_router(catalogs.router, prefix="/catalogs", tags=["Catalogs"])
api_router.include_router(financial.router, prefix="/financial", tags=["Financial"])
api_router.include_router(fiscal.router, prefix="/fiscal", tags=["Fiscal"])
api_router.include_router(inegi.router, prefix="/inegi", tags=["INEGI"])

# Spanish Prefixes (Aura Axioma Standard)
api_router.include_router(geo.router, prefix="/geografia", tags=["Geografía"])
api_router.include_router(catalogs.router, prefix="/catalogos", tags=["Catálogos"])
api_router.include_router(financial.router, prefix="/finanzas", tags=["Finanzas"])
api_router.include_router(fiscal.router, prefix="/fiscal", tags=["Fiscal"])
api_router.include_router(inegi.router, prefix="/inegi", tags=["INEGI"])
