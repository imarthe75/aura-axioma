from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.init_db import init_db
from app.core.auth import get_current_user
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.services.catalog_downloader import CatalogDownloader
import logging

app = FastAPI(
    title="Aura Axioma",
    description="Single Source of Truth for Master Catalogs (Geo, Fiscal, Financial) with SCD2 support.",
    version="1.0.0",
    root_path="/api",
    servers=[{"url": "https://axioma.casmart.internal/api", "description": "Production Gateway"}]
)

@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="aura-axioma-cache")
    except Exception as e:
        logging.error(f"Failed to initialize: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.api import api_router
app.include_router(api_router, prefix="/v1")

@app.get("/")
async def root():
    return {"message": "Aura Axioma API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/sync/initial", tags=["Admin"])
async def trigger_initial_sync(current_user: dict = Depends(get_current_user)):
    """Trigger the initial sync of all catalogs (Holidays, SEPOMEX, SAT, CASFIM)"""
    CatalogDownloader.sync_all_catalogs.delay()
    return {"status": "initial_sync_triggered"}
