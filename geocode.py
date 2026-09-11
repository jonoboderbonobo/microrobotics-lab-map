"""institution/city/country -> (lat, lon), backed by a committed disk cache.

Nominatim usage policy requires a descriptive User-Agent with a real contact
address, and at most one request per second -- see
https://operations.osmfoundation.org/policies/nominatim/
"""

import json
import math
import time
from pathlib import Path

import requests

CACHE_PATH = Path(__file__).parent / ".geocode-cache.json"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "microrobotics-lab-map/1.0 (contact: boerschmannjonas@gmail.com)"
DISAGREEMENT_THRESHOLD_M = 1000
REQUEST_INTERVAL_S = 1.0


def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    with CACHE_PATH.open() as f:
        return json.load(f)


def _save_cache(cache: dict) -> None:
    with CACHE_PATH.open("w") as f:
        json.dump(cache, f, indent=2, sort_keys=True)
        f.write("\n")


def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def resolve(institution: str, city: str, country: str) -> tuple[float, float]:
    """Geocode via Nominatim, cached by exact query string. Raises ValueError
    naming the query on zero results or disagreeing results. Never falls back
    to a default coordinate."""
    query = f"{institution}, {city}, {country}"
    cache = _load_cache()

    if query in cache:
        entry = cache[query]
        return entry["lat"], entry["lon"]

    response = requests.get(
        NOMINATIM_URL,
        params={"format": "jsonv2", "q": query},
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    time.sleep(REQUEST_INTERVAL_S)
    response.raise_for_status()
    results = response.json()

    if not results:
        raise ValueError(f"geocoding query returned zero results: {query!r}")

    lats = [float(r["lat"]) for r in results]
    lons = [float(r["lon"]) for r in results]
    if len(results) > 1:
        for lat, lon in zip(lats[1:], lons[1:]):
            if _haversine_m(lats[0], lons[0], lat, lon) > DISAGREEMENT_THRESHOLD_M:
                raise ValueError(
                    f"geocoding query returned disagreeing results (>{DISAGREEMENT_THRESHOLD_M}m apart): {query!r}"
                )

    lat, lon = round(lats[0], 5), round(lons[0], 5)
    cache[query] = {"lat": lat, "lon": lon}
    _save_cache(cache)
    return lat, lon
