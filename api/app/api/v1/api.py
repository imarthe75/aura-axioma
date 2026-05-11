from fastapi import APIRouter
from app.api.v1.endpoints import geo, catalogs, financial

api_router = APIRouter()
api_router.include_router(geo.router, prefix="/geo", tags=["Geo"])
api_router.include_router(catalogs.router, prefix="/catalogs", tags=["Catalogs"])
api_router.include_router(financial.router, prefix="/financial", tags=["Financial"])
