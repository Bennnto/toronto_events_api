from celery import shared_task

from .services import sync_db


@shared_task
def refresh_db():
    return sync_db()


@shared_task
def refresh_db_from_jsonld():
    import requests

    url = "https://raw.githubusercontent.com/TorontoOpenData/events/master/all.jsonld"
    file_path = "toronto_docs/all.jsonld"

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    if resp.status_code == 200:
        with open(file_path, "w") as f:
            f.write(resp.text)

    from .management.commands.import_jsonld import Command

    cmd = Command()
    cmd.handle(file=file_path, commit=True)
