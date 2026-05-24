from django.core.management.base import BaseCommand
from event_app.services import sync_db
from event_app.management.commands.import_jsonld import Command as ImportJsonldCommand


class Command(BaseCommand):
    help = "Import events from Ticketmaster API and JSON-LD sources (dry-run by default)"

    def add_arguments(self, parser):
        parser.add_argument("--commit", action="store_true", help="Persist changes to the DB")

    def handle(self, *args, **options):
        self.stdout.write("Running Ticketmaster sync...")
        tm_result = sync_db()
        self.stdout.write(f"Ticketmaster sync result: {tm_result}")

        self.stdout.write("\nRunning JSON-LD import (dry-run unless --commit)...")
        importer = ImportJsonldCommand()
        importer.handle(file="toronto_docs/all.jsonld", commit=options.get("commit", False))
