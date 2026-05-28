from fastapi import APIRouter
from app.api.v1.endpoints import geo, catalogs, financial, fiscal, inegi, admin

api_router = APIRouter()

# Single canonical prefix set — Spanish/English aliases removed to avoid Swagger duplication
api_router.include_router(geo.router,       prefix="/geo",       tags=["Geografía"])
api_router.include_router(catalogs.router,  prefix="/catalogs",  tags=["Catálogos"])
api_router.include_router(financial.router, prefix="/financial", tags=["Finanzas"])
api_router.include_router(fiscal.router,    prefix="/fiscal",    tags=["Fiscal"])
api_router.include_router(inegi.router,     prefix="/inegi",     tags=["INEGI"])
api_router.include_router(admin.router,     prefix="/admin",     tags=["Administración"])
