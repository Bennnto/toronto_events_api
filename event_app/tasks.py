from celery import shared_task
from .services import sync_db
from django.utils import timezone
from datetime import timedelta
from .models import Event


@shared_task
def refresh_db():
    return sync_db()


@shared_task
def refresh_db_from_jsonld():
    import requests
    import os
    from pathlib import Path

    url = "https://raw.githubusercontent.com/TorontoOpenData/events/master/all.jsonld"
    file_path = Path("toronto_docs/all.jsonld")

    # Try fetching remote file; if it fails, fall back to local file if present
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open("w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"Downloaded remote JSON-LD to {file_path}")
        else:
            print(f"Remote returned status {resp.status_code}; will try local file if available")
    except requests.RequestException as e:
        print(f"Failed to fetch remote JSON-LD: {e}; will try local file if available")

    if not file_path.exists():
        print(f"No JSON-LD file available at {file_path}; aborting import")
        return {"error": "no_source_file"}

    from .management.commands.import_jsonld import Command
    cmd = Command()
    cmd.handle(file=str(file_path), commit=True)



@shared_task
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
    