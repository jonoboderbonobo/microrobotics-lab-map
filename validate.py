"""Schema and referential validation for labs.yaml. Raises ValueError naming
the offending record's id on any problem. No silent skipping."""

import re

from taxonomy import APPLICATIONS, CATEGORIES, INSTITUTION_TYPES, STATUSES

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
COUNTRY_RE = re.compile(r"^[A-Z]{2}$")
OSM_RE = re.compile(r"^(way|relation)/\d+$")

# Every field key is always present in a record; nullability is checked
# per-field below rather than via a separate optional-fields set.
ALL_FIELDS = {
    "id", "name", "pi", "institution", "city", "country", "lat", "lon", "osm",
    "url", "people_url", "category", "application", "min_dim_um",
    "onboard_power", "institution_type", "relevance", "status",
    "description", "notes",
}


def _fail(lab_id, message):
    raise ValueError(f"{lab_id}: {message}")


def _check_url(lab_id, field, value, required=True):
    if value is None:
        if required:
            _fail(lab_id, f"{field} is required")
        return
    if not isinstance(value, str) or not (value.startswith("http://") or value.startswith("https://")):
        _fail(lab_id, f"{field} must start with http:// or https://, got {value!r}")


def validate(labs) -> None:
    if not isinstance(labs, list):
        raise ValueError("labs.yaml must contain a YAML list")

    seen_ids = set()
    for lab in labs:
        if not isinstance(lab, dict) or "id" not in lab:
            raise ValueError(f"record missing id: {lab!r}")
        lab_id = lab["id"]

        if not isinstance(lab_id, str) or not ID_RE.match(lab_id):
            _fail(lab_id, "id must match ^[a-z0-9]+(-[a-z0-9]+)*$")
        if lab_id in seen_ids:
            _fail(lab_id, "duplicate id")
        seen_ids.add(lab_id)

        missing = ALL_FIELDS - lab.keys()
        if missing:
            _fail(lab_id, f"missing required field(s): {sorted(missing)}")
        unexpected = lab.keys() - ALL_FIELDS
        if unexpected:
            _fail(lab_id, f"unexpected field(s): {sorted(unexpected)}")

        for field in ("name", "institution", "city"):
            if not isinstance(lab[field], str) or not lab[field]:
                _fail(lab_id, f"{field} must be a non-empty string")

        if lab["pi"] is not None and not isinstance(lab["pi"], str):
            _fail(lab_id, "pi must be a string or null")

        if not isinstance(lab["country"], str) or not COUNTRY_RE.match(lab["country"]):
            _fail(lab_id, "country must be two uppercase letters (ISO 3166-1 alpha-2)")

        lat, lon = lab["lat"], lab["lon"]
        if (lat is None) != (lon is None):
            _fail(lab_id, "lat and lon must both be null or both be set")
        if lat is not None:
            if not isinstance(lat, (int, float)) or not (-90 <= lat <= 90):
                _fail(lab_id, f"lat must be in -90..90, got {lat!r}")
            if not isinstance(lon, (int, float)) or not (-180 <= lon <= 180):
                _fail(lab_id, f"lon must be in -180..180, got {lon!r}")

        osm = lab["osm"]
        if osm is not None and (not isinstance(osm, str) or not OSM_RE.match(osm)):
            _fail(lab_id, f"osm must be null or match ^(way|relation)/<id>$, got {osm!r}")

        _check_url(lab_id, "url", lab["url"], required=True)
        _check_url(lab_id, "people_url", lab.get("people_url"), required=False)

        if lab["category"] not in CATEGORIES:
            _fail(lab_id, f"category must be one of {sorted(CATEGORIES)}, got {lab['category']!r}")

        applications = lab["application"]
        if not isinstance(applications, list):
            _fail(lab_id, "application must be a list")
        for value in applications:
            if value not in APPLICATIONS:
                _fail(lab_id, f"application value {value!r} not in {sorted(APPLICATIONS)}")

        min_dim_um = lab["min_dim_um"]
        if min_dim_um is not None and not isinstance(min_dim_um, int):
            _fail(lab_id, "min_dim_um must be an int or null")

        if not isinstance(lab["onboard_power"], bool):
            _fail(lab_id, "onboard_power must be a boolean")

        if lab["institution_type"] not in INSTITUTION_TYPES:
            _fail(lab_id, f"institution_type must be one of {sorted(INSTITUTION_TYPES)}, got {lab['institution_type']!r}")

        relevance = lab["relevance"]
        if not isinstance(relevance, int) or isinstance(relevance, bool) or not (1 <= relevance <= 5):
            _fail(lab_id, f"relevance must be an int in 1..5, got {relevance!r}")

        if lab["status"] not in STATUSES:
            _fail(lab_id, f"status must be one of {sorted(STATUSES)}, got {lab['status']!r}")

        for field in ("description", "notes"):
            if lab[field] is not None and not isinstance(lab[field], str):
                _fail(lab_id, f"{field} must be a string or null")

    ids_in_order = [lab["id"] for lab in labs]
    if ids_in_order != sorted(ids_in_order):
        raise ValueError(
            "labs.yaml is not sorted by id. Run `python build.py --sort` to fix in place."
        )
