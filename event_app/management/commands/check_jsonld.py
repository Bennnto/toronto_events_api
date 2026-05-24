from django.core.management.base import BaseCommand
import os
import json
import requests
from pathlib import Path

DEFAULT_URLS = [
    "https://raw.githubusercontent.com/TorontoOpenData/events/main/all.jsonld",
    "https://raw.githubusercontent.com/TorontoOpenData/events/master/all.jsonld",
]


class Command(BaseCommand):
    help = "Check JSON-LD sources and local fallback file counts"

    def add_arguments(self, parser):
        parser.add_argument("--local-only", action="store_true", help="Only check the local fallback file")

    def handle(self, *args, **options):
        urls_env = os.getenv("JSONLD_SOURCE_URLS") or os.getenv("JSONLD_SOURCE_URL")
        if urls_env:
            urls = [u.strip() for u in urls_env.split(",") if u.strip()]
        else:
            urls = DEFAULT_URLS

        self.stdout.write("Configured remote JSON-LD URLs:")
        for u in urls:
            self.stdout.write(f" - {u}")

        if not options.get("local_only"):
            self.stdout.write("\nChecking remote URLs (timeout=10s):")
            for u in urls:
                try:
                    resp = requests.get(u, timeout=10)
                    if resp.status_code == 200:
                        # try to parse as JSON to count items if possible
                        try:
                            data = resp.json()
                            if isinstance(data, list):
                                self.stdout.write(f"  OK: {u} -> {len(data)} items")
                            else:
                                self.stdout.write(f"  OK: {u} -> status 200 (not an array)")
                        except Exception:
                            self.stdout.write(f"  OK: {u} -> status 200 (non-json response)")
                    else:
                        self.stdout.write(f"  {resp.status_code}: {u}")
                except Exception as e:
                    self.stdout.write(f"  Error: {u} -> {e}")

        # Local fallback
        local_path = Path("toronto_docs/all.jsonld")
        if local_path.exists():
            try:
                with local_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                count = len(data) if isinstance(data, list) else "not-an-array"
            except Exception as e:
                count = f"error reading file: {e}"
        else:
            count = "missing"

        self.stdout.write(f"\nLocal fallback file: {local_path} -> {count}")
