from celery import shared_task
from .services import sync_db
from django.utils import timezone
from datetime import timedelta
from pathlib import Path
from .models import Event
from celery import shared_task


JSONLD_SOURCE_URLS = [
    "https://raw.githubusercontent.com/TorontoOpenData/events/main/all.jsonld",
    "https://raw.githubusercontent.com/TorontoOpenData/events/master/all.jsonld",
]
JSONLD_FALLBACK_PATH = Path("toronto_docs/all.jsonld")


@shared_task(name="event_app.tasks.refresh_db")
def refresh_db():
    return sync_db()


@shared_task(name="event_app.tasks.refresh_db_from_jsonld")
def refresh_db_from_jsonld():
    import requests
    import os

        # Allow overriding the list of source URLs via environment variable
        env_urls = os.getenv("JSONLD_SOURCE_URLS") or os.getenv("JSONLD_SOURCE_URL")
        if env_urls:
            urls = [u.strip() for u in env_urls.split(",") if u.strip()]
        else:
            urls = JSONLD_SOURCE_URLS

        file_path = JSONLD_FALLBACK_PATH

        # Try fetching the remote file first; if that fails, fall back to any local copy.
        downloaded = False
        for url in urls:
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            if resp.status_code == 200:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with file_path.open("w", encoding="utf-8") as f:
                    f.write(resp.text)
                print(f"Downloaded remote JSON-LD from {url} to {file_path}")
                downloaded = True
                break
        except requests.HTTPError as e:
            print(f"Remote JSON-LD at {url} returned HTTP error: {e}; trying next")
        except requests.RequestException as e:
            print(f"Failed to fetch remote JSON-LD from {url}: {e}; trying next")

    if not file_path.exists():
        print(f"No JSON-LD file available at {file_path}; aborting import")
        return {"error": "no_source_file"}

    from .management.commands.import_jsonld import Command
    cmd = Command()
    cmd.handle(file=str(file_path), commit=True)


@shared_task(name="event_app.tasks.import_all_sources_task")
def import_all_sources_task(commit: bool = False):
    """Run Ticketmaster sync and JSON-LD import together. Intended for periodic/automated runs."""
    results = {"ticketmaster": None, "jsonld": None}

    try:
        results["ticketmaster"] = sync_db()
    except Exception as e:
        results["ticketmaster"] = {"error": str(e)}

    try:
        from .management.commands.import_jsonld import Command

        cmd = Command()
        cmd.handle(file=str(JSONLD_FALLBACK_PATH), commit=commit)
        results["jsonld"] = {"imported": True}
    except Exception as e:
        results["jsonld"] = {"error": str(e)}

    return results



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
    