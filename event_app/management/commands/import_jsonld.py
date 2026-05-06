from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decimal import Decimal
import json
from pathlib import Path
import importlib.util


class Command(BaseCommand):
    help = "Import events from a JSON-LD file using event_app/json-mapper.py"

    def add_arguments(self, parser):
        parser.add_argument("--file", "-f", required=True, help="Path to all.jsonld")
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Actually write to DB (dry-run by default)",
        )
        parser.add_argument(
            "--batch-size", type=int, default=200, help="Batch size for bulk operations"
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        mapper_path = Path("event_app/json-mapper.py")
        if not mapper_path.exists():
            raise CommandError(
                f"Mapper not found at {mapper_path} (expected event_app/json-mapper.py)"
            )

        spec = importlib.util.spec_from_file_location("json_mapper", mapper_path)
        json_mapper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(json_mapper)

        from event_app.models import Venue, Category, Event, Offer

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        total = len(data)
        self.stdout.write(f"Loaded {total} items from {path}")

        counters = {
            "venue": 0,
            "category": 0,
            "event": 0,
            "offer": 0,
            "skipped": 0,
            "errors": 0,
        }

        for idx, item in enumerate(data, start=1):
            try:
                payload = json_mapper.map_jsonld(item)
            except Exception as e:
                counters["errors"] += 1
                self.stderr.write(f"[{idx}] mapper error: {e}")
                continue

            ev = payload.get("event", {})
            vn = payload.get("venue", {})
            cat = payload.get("category", {})
            offer = payload.get("offer")

            if not ev.get("ext_id"):
                counters["skipped"] += 1
                continue

            if options.get("commit"):
                try:
                    with transaction.atomic():
                        venue_obj, v_created = Venue.objects.get_or_create(
                            venue_name=vn.get("venue_name") or "Unknown",
                            defaults={
                                "venue_type": vn.get("venue_type") or "",
                                "seat_map": vn.get("seat_map") or "",
                                "address": vn.get("address") or "",
                                "city": vn.get("city") or "",
                                "country": vn.get("country") or "",
                                "latitude": Decimal(str(vn.get("latitude")))
                                if vn.get("latitude") not in (None, "")
                                else Decimal("0.0"),
                                "longitude": Decimal(str(vn.get("longitude")))
                                if vn.get("longitude") not in (None, "")
                                else Decimal("0.0"),
                            },
                        )
                        if v_created:
                            counters["venue"] += 1

                        category_obj, c_created = Category.objects.get_or_create(
                            segment=cat.get("segment") or "Other",
                            defaults={
                                "genre": cat.get("genre") or "",
                                "subgenre": cat.get("subgenre") or "",
                            },
                        )
                        if c_created:
                            counters["category"] += 1

                        event_defaults = {
                            "event_name": ev.get("event_name") or "",
                            "description": ev.get("description") or "",
                            "event_url": ev.get("event_url"),
                            "category": category_obj,
                            "venue": venue_obj,
                            "sale_status": ev.get("sale_status"),
                            "sale_start_date": ev.get("sale_start_date"),
                            "sale_end_date": ev.get("sale_end_date"),
                            "event_start_date": ev.get("event_start_date") or None,
                        }

                        event_obj, e_created = Event.objects.update_or_create(
                            ext_id=ev.get("ext_id"),
                            defaults=event_defaults,
                        )
                        if e_created:
                            counters["event"] += 1

                        if offer and offer.get("sale_url"):
                            Offer.objects.update_or_create(
                                event=event_obj,
                                sale_url=offer.get("sale_url"),
                                defaults={
                                    "offer_type": offer.get("offer_type"),
                                    "price": offer.get("price"),
                                    "currency": offer.get("currency"),
                                },
                            )
                            counters["offer"] += 1
                except Exception as e:
                    counters["errors"] += 1
                    self.stderr.write(f"[{idx}] DB error: {e}")
            else:
                self.stdout.write(
                    f"[{idx}/{total}] ext_id={ev.get('ext_id')} event_name={ev.get('event_name')!r} offer={bool(offer)}"
                )

        self.stdout.write("\nSummary:")
        for k, v in counters.items():
            self.stdout.write(f"  {k}: {v}")

        if not options.get("commit"):
            self.stdout.write(
                "\nDry-run complete. Rerun with --commit to persist changes."
            )
