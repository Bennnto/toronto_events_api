from hashlib import sha1
from datetime import datetime, timezone

def _to_dt(value):
    if not value :
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _safe(d, *path, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default

def build_ext_id(item: dict) -> str:
    base = f"{item.get('url', '')}|{item.get('startDate', '')}|{item.get('name', '')}"
    return sha1(base.encode("utf-8")).hexdigest()

def _first_offer(item: dict) -> dict:
    offers = item.get('offers')
    if isinstance(offers, list):
        return offers[0] if offers else {}
    if isinstance(offers, dict):
        return offers
    return {}

def map_jsonld(item: dict) -> dict:
    keywords = item.get("keywords") or []
    location = item.get("location") or {}
    address = location.get("address") or {}
    geo = location.get("geo") or {}
    offer = _first_offer(item)
    
    offer_payload = None
    if offer:
        offer_payload = {
            "offer_type": offer.get('@type'),
            "price": offer.get("price"),
            "currency": offer.get("priceCurrency"),
            "sale_url": offer.get('url')
        }
    return { 
        "event": {
            "ext_id": build_ext_id(item),
            "event_name":item.get('name', ""),
            "description": item.get('description', ""),
            "event_url": item.get('url'),
            'sale_url': _safe(item, 'offers', "url", default=item.get("url")),
            "sale_status": "ON_SALE" if item.get("offer") else "NOT_FOR_SALE",
            "sale_start_date": None,
            "sale_end_date": None,
            "event_start_date": _to_dt(item.get("startDate")),
        },
        "venue": {
            "venue_name": location.get('name', 'Unknown'),
            "venue_type": location.get('@type'),
            "seat_map": None,
            "address": address.get("streetAddress"),
            "city": address.get('addresssLocality'),
            "country": address.get('addressCountry'),
            "latitude": geo.get('latitude'),
            "longitude": geo.get('longitude'),   
        },
        "category": {
            "segment": item.get('keywords', [])[0] if len(keywords) > 0 else "Other",
            "genre": item.get('keywords', [])[1] if len(keywords) > 1 else "Other",
            "subgenre": item.get('keywords', [])[2] if len(keywords) > 2 else "",
        },
        "offer": offer_payload,
    }