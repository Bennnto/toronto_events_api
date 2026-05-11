import os
from celery import Celery
from celery.signals import worker_init, worker_process_init
from django.db import connections

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "events.settings")

app = Celery("events")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Safer default worker settings (can be overridden via env vars / CLI)
app.conf.worker_max_tasks_per_child = int(os.getenv("CELERY_MAX_TASKS_PER_CHILD", "100"))
app.conf.worker_prefetch_multiplier = int(os.getenv("CELERY_PREFETCH_MULTIPLIER", "1"))
app.conf.worker_disable_rate_limits = bool(int(os.getenv("CELERY_DISABLE_RATE_LIMITS", "1")))

from celery.signals import worker_shutdown
import logging

logger = logging.getLogger(__name__)


@worker_shutdown.connect
def log_worker_shutdown(sig=None, how=None, exitcode=None, **kwargs):
	logger.warning("Celery worker_shutdown signal received: sig=%r how=%r exitcode=%r", sig, how, exitcode)


@worker_init.connect
def close_db_connections_worker_init(**kwargs):
	# Close any Django DB connections in the parent worker process before forking
	try:
		connections.close_all()
	except Exception:
		pass


@worker_process_init.connect
def close_db_connections_worker_process_init(**kwargs):
	# Ensure child worker process has no inherited DB connections
	try:
		connections.close_all()
	except Exception:
		pass
