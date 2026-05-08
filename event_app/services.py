import requests
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv


# ----------------- load environment variable ---------------- #
load_dotenv()
TK_MT_URL = os.getenv("TK_MT_URL")
TK_MT_API_KEY = os.getenv("TK_MT_API")


# ------------------ Parse DateTime isoformat --------------------#
def parse_iso_datetime(dt_string):
    """Convert ISO format datetime string to Python datetime object"""
    if dt_string is None or dt_string == "":
        return None
    try:
        # Handle ISO format strings like "2026-06-12T19:00:00Z"
        if isinstance(dt_string, str):
            # Remove 'Z' and parse
            dt_string = dt_string.replace("Z", "+00:00")
            return datetime.fromisoformat(dt_string)
        return dt_string
    except Exception as e:
        print(f'⚠️ Failed to parse datetime "{dt_string}": {e}')
        return None


# ------------------ Fetch external Api (Ticketmaster APIs) -------------- #
def fetch_api(page=0):
    params = {
        "apikey": TK_MT_API_KEY,
        "city": "Toronto",
        "size": 200,  # Max results per page
        "page": page,
    }
    try:
        print(f"Fetching page {page}...")
        resp = requests.get(TK_MT_URL, params=params, timeout=20)
        resp.raise_for_status()
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("✅ Reached end of results")
            return None
        print(f"❌ API Error: {type(e).__name__}: {e}")
        return None
    except Exception as e:
        print(f"❌ API Error: {type(e).__name__}: {e}")
        return None


def parse_raw_data():
    all_events = []
    page = 0

    while True:
        raw_data = fetch_api(page)
        if raw_data is None:
            if page == 0:
                print("⚠️ Couldn't fetch any data from API")
            else:
                print(
                    f"✅ Last page reached after page {page - 1}, collected {len(all_events)} events"
                )
            break

        event_data = raw_data.get("_embedded", {}).get("events", [])
        if not event_data:
            print(f"✅ Fetched {len(all_events)} total events")
            break

        for event in event_data:
            id = event.get("id", "")
            name = event.get("name", "Unknown")
            description = event.get("description", "")
            event_url = event.get("url", "")
            outlets = event.get("outlets") or []
            sale_url = outlets[0].get("url", "") if outlets else ""
            event_start_date = (
                event.get("dates", {}).get("start", {}).get("dateTime") or None
            )
            event_start_date = parse_iso_datetime(event_start_date)
            sale_start_date = (
                event.get("sales", {}).get("public", {}).get("startDateTime") or None
            )
            sale_start_date = parse_iso_datetime(sale_start_date)
            sale_end_date = (
                event.get("sales", {}).get("public", {}).get("endDateTime") or None
            )
            sale_end_date = parse_iso_datetime(sale_end_date)
            # Derive sale_status from sale dates
            if sale_start_date and sale_end_date:
                sale_status = "ON_SALE"
            elif sale_start_date:
                sale_status = "UPCOMING_SALE"
            else:
                sale_status = "NOT_ON_SALE"
            venues = event.get("_embedded", {}).get("venues", [])
            venue = venues[0] if venues else {}
            venue_type = venue.get("type", "venue")
            venue_name = venue.get("name", "Unknown")
            address = (
                venue.get("address", {}).get("line1", "")
                if venue.get("address")
                else ""
            )
            city = (
                venue.get("city", {}).get("name", "Unknown")
                if venue.get("city")
                else "Unknown"
            )
            country = (
                venue.get("country", {}).get("name", "Unknown")
                if venue.get("country")
                else "Unknown"
            )
            latitude = venue.get("location", {}).get("latitude", "0")
            longitude = venue.get("location", {}).get("longitude", "0")
            seatmap = (
                venue.get("seatmap", {}).get("staticUrl", "")
                if venue.get("seatmap")
                else ""
            )

            classifications = event.get("classifications") or []
            category = classifications[0] if classifications else {}
            segment = (category.get("segment") or {}).get("name", "Other")
            genre = (category.get("genre") or {}).get("name", "Other")
            subgenre = (category.get("subGenre") or {}).get("name", "Other")

            parsed_data = {
                "ext_id": id,
                "event_name": name,
                "description": description,
                "event_url": event_url,
                "sale_url": sale_url,
                "venue_name": venue_name,
                "venue_type": venue_type,
                "address": address,
                "city": city,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
                "seat_map": seatmap,
                "segment": segment,
                "genre": genre,
                "subgenre": subgenre,
                "sale_start_date": sale_start_date,
                "sale_end_date": sale_end_date,
                "event_start_date": event_start_date,
                "sale_status": sale_status,
            }
            all_events.append(parsed_data)

        # Check if there are more pages
        page_info = raw_data.get("page", {})
        if page >= page_info.get("totalPages", 0) - 1:
            print(f"✅ Fetched {len(all_events)} total events")
            break

        page += 1

    return all_events


def sync_db():
    parsed_data = parse_raw_data()
    if not parsed_data:
        print("⚠️ Couldn't Fetch Data from API")
        return None

    synced = {"event": 0, "venue": 0, "category": 0, "error": 0}

    from .models import Venue, Category, Event, Offer

    for data in parsed_data:

        def to_decimal(val):
            try:
                return Decimal(str(val)) if val not in (None, "") else Decimal("0.0")
            except InvalidOperation:
                return Decimal("0.0")

        venue, v_created = Venue.objects.get_or_create(
            venue_name=data.get("venue_name") or "Unknown",
            defaults={
                "venue_type": data.get("venue_type") or "",
                "seat_map": data.get("seat_map") or "",
                "address": data.get("address") or "",
                "city": data.get("city") or "",
                "country": data.get("country") or "",
                "latitude": to_decimal(data.get("latitude")),
                "longitude": to_decimal(data.get("longitude")),
            },
        )
        if v_created:
            synced["venue"] += 1
            print(f"created {venue.venue_name}")

        category, c_created = Category.objects.update_or_create(
            segment=data.get("segment") or "Other",
            defaults={
                "genre": data.get("genre") or "",
                "subgenre": data.get("subgenre") or "",
            },
        )
        if c_created:
            synced["category"] += 1
            print(f"created {category.segment}")

        event, e_created = Event.objects.update_or_create(
            ext_id=data.get("ext_id"),
            defaults={
                "event_name": data.get("event_name") or "",
                "description": data.get("description") or "",
                "event_url": data.get("event_url"),
                "category": category,
                "venue": venue,
                "sale_status": data.get("sale_status"),
                "sale_start_date": data.get("sale_start_date"),
                "sale_end_date": data.get("sale_end_date"),
                "event_start_date": data.get("event_start_date"),
            },
        )
        if e_created:
            synced["event"] += 1
            print(f"created {event.event_name}")
        # Create or update Offer record if we have a sale URL
        try:
            sale_url = data.get("sale_url")
            if sale_url:
                # Ticketmaster parsed data currently does not include price/currency in parsed_data.
                # Create a simple Offer linking to this Event.
                Offer.objects.update_or_create(
                    event=event,
                    sale_url=sale_url,
                    defaults={
                        "price": data.get("price"),
                        "currency": data.get("priceCurrency"),
                        "offer_type": "ticket",
                    },
                )
        except Exception as e:
            synced["error"] += 1
            print(f"Failed to create/update Offer for event {event.ext_id}: {e}")

    return synced
