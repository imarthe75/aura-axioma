from celery import Celery
from celery.schedules import crontab
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://casmarts-core-cache:6379/2")

celery_app = Celery(
    "aura_axioma",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.services.catalog_downloader"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Mexico_City",
    enable_utc=True,
)

# Schedule weekly sync (Sunday at 2:00 AM)
celery_app.conf.beat_schedule = {
    "sync-all-catalogs-weekly": {
        "task": "app.services.catalog_downloader.sync_all_catalogs",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),
    },
}
