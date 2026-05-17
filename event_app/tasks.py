from celery import shared_task
from .services import sync_db
from django.utils import timezone
from datetime import timedelta
from pathlib import Path
from .models import Event


JSONLD_SOURCE_URL = "https://raw.githubusercontent.com/TorontoOpenData/events/main/all.jsonld"
JSONLD_FALLBACK_PATH = Path("toronto_docs/all.jsonld")


@shared_task(name="event_app.tasks.refresh_db")
def refresh_db():
    return sync_db()


@shared_task(name="event_app.tasks.refresh_db_from_jsonld")
def refresh_db_from_jsonld():
    import requests

    file_path = JSONLD_FALLBACK_PATH

    # Try fetching the remote file first; if that fails, fall back to any local copy.
    try:
        resp = requests.get(JSONLD_SOURCE_URL, timeout=20)
        resp.raise_for_status()
        if resp.status_code == 200:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open("w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"Downloaded remote JSON-LD to {file_path}")
    except requests.HTTPError as e:
        print(f"Remote JSON-LD returned HTTP error: {e}; will try local file if available")
    except requests.RequestException as e:
        print(f"Failed to fetch remote JSON-LD: {e}; will try local file if available")

    if not file_path.exists():
        print(f"No JSON-LD file available at {file_path}; aborting import")
        return {"error": "no_source_file"}

    from .management.commands.import_jsonld import Command
    cmd = Command()
    cmd.handle(file=str(file_path), commit=True)



@shared_task(name="event_app.tasks.cleanup_past_events")
def cleanup_past_events(retention_days: int = 0):
    """Remove events whose `event_start_date` is older than now or older than
    `retention_days` if provided. Returns number of deleted events."""
    now = timezone.now()
    if retention_days and retention_days > 0:
        cutoff = now - timedelta(days=retention_days)
    else:
        cutoff = now

    qs = Event.objects.filter(event_start_date__lt=cutoff)
    deleted_count = qs.count()
    qs.delete()
    return {"deleted": deleted_count}
    