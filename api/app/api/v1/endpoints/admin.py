from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.services.scd2_manager import SCD2Manager
from app.core.auth import get_current_user
from app.services.catalog_downloader import CatalogDownloader
import datetime

router = APIRouter()

@router.get("/status", tags=["Administración"])
async def get_admin_status(current_user: dict = Depends(get_current_user)):
    """
    Return system health: Celery worker status, DB connectivity,
    last sync timestamps per catalog, and the next scheduled sync time.
    """
    manager = SCD2Manager(target_table="asentamientos", natural_key="id", schema="geo")
    db_ok = False
    catalogs_info = {}

    try:
        with manager.engine.connect() as conn:
            db_ok = True

            for schema, table, label in [
                ("geo",       "asentamientos",          "SEPOMEX / Geo"),
                ("fiscal",    "cat_prod_serv",          "SAT / Fiscal"),
                ("financial", "instituciones_bancarias", "CASFIM / Bancos"),
                ("calendars", "holidays",               "Calendarios"),
                ("fiscal",    "cat_bancos",             "Bancos SAT"),
                ("fiscal",    "cat_paises",             "Países SAT"),
            ]:
                try:
                    row = conn.execute(text(f"""
                        SELECT 
                            COUNT(*) FILTER (WHERE scd_is_current = TRUE)  AS vigentes,
                            COUNT(*) FILTER (WHERE scd_is_current = FALSE) AS historicos,
                            MAX(scd_start_date) FILTER (WHERE scd_is_current = TRUE) AS ultima_sync,
                            MAX(scd_version)    FILTER (WHERE scd_is_current = TRUE) AS max_version
                        FROM {schema}.{table}
                    """)).mappings().fetchone()
                    catalogs_info[schema] = {
                        "label": label,
                        "tabla": f"{schema}.{table}",
                        "vigentes": row["vigentes"] or 0,
                        "historicos": row["historicos"] or 0,
                        "ultima_sync": row["ultima_sync"].isoformat() if row["ultima_sync"] else None,
                        "max_version": row["max_version"] or 1,
                        "status": "ok",
                    }
                except Exception as e:
                    catalogs_info[schema] = {"label": label, "status": "error", "error": str(e)}

    except Exception as e:
        catalogs_info = {"error": str(e)}

    # Celery worker connectivity check via ping
    worker_ok = False
    worker_info = []
    try:
        from app.core.celery_app import celery_app
        inspect = celery_app.control.inspect(timeout=3)
        ping_result = inspect.ping() or {}
        worker_ok = len(ping_result) > 0
        worker_info = list(ping_result.keys())
    except Exception as e:
        worker_info = [f"Error: {e}"]

    # Calculate next Sunday 02:00 AM Mexico City time
    now_utc = datetime.datetime.utcnow()
    # Sunday = 6 in Python weekday (Mon=0)
    days_until_sunday = (6 - now_utc.weekday()) % 7
    if days_until_sunday == 0 and now_utc.hour >= 8:  # Already past 02:00 CST (08:00 UTC)
        days_until_sunday = 7
    next_sync_utc = (now_utc + datetime.timedelta(days=days_until_sunday)).replace(
        hour=8, minute=0, second=0, microsecond=0
    )

    return {
        "sistema": {
            "db_status": "ok" if db_ok else "error",
            "celery_worker": "ok" if worker_ok else "disconnected",
            "workers_activos": worker_info,
            "timestamp": now_utc.isoformat() + "Z",
        },
        "proxima_sync_automatica": {
            "schedule": "Domingos 02:00 AM (America/Mexico_City)",
            "proxima_ejecucion_utc": next_sync_utc.isoformat() + "Z",
            "dias_restantes": days_until_sunday,
        },
        "catalogos": catalogs_info,
    }


@router.post("/sync", tags=["Administración"])
async def trigger_sync_from_admin(current_user: dict = Depends(get_current_user)):
    """Trigger a full catalog synchronization from the Admin panel."""
    try:
        task = CatalogDownloader.sync_all_catalogs.delay()
        return {"status": "triggered", "task_id": task.id, "message": "Sincronización iniciada en background."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
