from celery import shared_task

from .services import sync_db


@shared_task
def refresh_db():
    return sync_db()


@shared_task
def refresh_db_from_jsonld():
    import os
    import requests

    base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
    package_url = base_url + "/api/3/action/package_show"
    params = {"id": "festivals-events"}
    
    package = requests.get(package_url, params=params, timeout=10).json()
    download_url = None
    
    # Find the JSON resource
    for idx, resource in enumerate(package["result"]["resources"]):
        if not resource["datastore_active"] and resource["format"].lower() == "json":
            res_url = base_url + "/api/3/action/resource_show?id=" + resource["id"]
            resource_metadata = requests.get(res_url, timeout=10).json()
            download_url = resource_metadata["result"]["url"]
            break

    if download_url:
        # Download the file
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        resp = requests.get(download_url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        if resp.status_code == 200:
            file_path = "toronto_docs/all.jsonld"
            # Ensure the directory exists so it doesn't crash
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w") as f:
                f.write(resp.text)

            from .management.commands.import_jsonld import Command

            cmd = Command()
            cmd.handle(file=file_path, commit=True)
