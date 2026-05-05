from celery import shared_task
from .services import sync_db

@shared_task
def refresh_db():
    return sync_db()

