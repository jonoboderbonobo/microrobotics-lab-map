#!/usr/bin/env python3
"""labs.yaml -> out/*.geojson. Single command: `python build.py`.

`python build.py --sort` re-sorts labs.yaml by id in place and exits; this is
what validate.py's error message points you to when the sort-order check fails.
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

import geocode
from taxonomy import CATEGORIES, ICON_SHAPE, POLYGON_OPTIONS
from validate import validate

ROOT = Path(__file__).parent
LABS_PATH = ROOT / "labs.yaml"
OUT_DIR = ROOT / "out"
POLYGONS_DIR = ROOT / "polygons"


def load_labs() -> list:
    with LABS_PATH.open() as f:
        return yaml.safe_load(f) or []


def save_labs(labs: list) -> None:
    with LABS_PATH.open("w") as f:
        yaml.safe_dump(labs, f, sort_keys=False, allow_unicode=True)


def resolve_missing_coordinates(labs: list) -> bool:
    changed = False
    for lab in labs:
        if lab["lat"] is None or lab["lon"] is None:
            lat, lon = geocode.resolve(lab["institution"], lab["city"], lab["country"])
            lab["lat"], lab["lon"] = lat, lon
            changed = True
    return changed


def build_description(lab: dict, category_label: str) -> str:
    """Builds the public uMap popup text. `lab['notes']` is a private
    assessment and must never be read here -- only `lab['description']`,
    `lab['interesting_work']`, `lab['community_improvement']`, and
    `lab['mission_fit']` (all public commentary, unlike `notes`) are
    rendered into the popup."""
    header = f"**{lab['pi']}**" if lab["pi"] else f"**{lab['name']}**"
    header += f" — {lab['institution']}, {lab['city']} ({lab['country']})"
    lines = [header]

    if lab.get("image"):
        # uMap's toHTML (umap/static/umap/js/modules/utils.js) turns a bare
        # {{https://...}} into <img src="...">; img/src/style are on its
        # DOMPurify allow-list, so this survives sanitization and renders.
        lines += ["", f"{{{{{lab['image']}}}}}"]

    if lab.get("description"):
        lines += ["", lab["description"].strip()]

    if lab.get("interesting_work"):
        lines += ["", f"**Latest research/products of interest:** {lab['interesting_work'].strip()}"]

    if lab.get("community_improvement"):
        lines += ["", f"**How this could improve the microrobotics community:** {lab['community_improvement'].strip()}"]

    if lab.get("mission_fit"):
        lines += ["", f"**Why it's on this map:** {lab['mission_fit'].strip()}"]

    links = [f"[[{lab['url']}|Group website]]"]
    if lab.get("people_url"):
        links.append(f"[[{lab['people_url']}|People]]")
    lines += ["", *links]

    min_dim = f"{lab['min_dim_um']} µm" if lab["min_dim_um"] is not None else "unknown"
    lines += ["", f"Category: {category_label} · Smallest demonstrated: {min_dim}"]

    # uMap's popup renderer (toHTML in umap/static/umap/js/modules/utils.js)
    # never turns "\n" into a visual break -- no markup rule does it, and no
    # popup CSS sets white-space: pre-line either. "br" is on its DOMPurify
    # allow-list, so replace every newline (including ones folded into
    # multi-paragraph `description`/`notes` text) with a literal <br>.
    return "\n".join(lines).replace("\n", "<br>")


def build_properties(lab: dict) -> dict:
    category_label, color, _ = CATEGORIES[lab["category"]]
    return {
        "name": lab["name"],
        "description": build_description(lab, category_label),
        "id": lab["id"],
        "pi": lab["pi"] or "",
        "institution": lab["institution"],
        "country": lab["country"],
        "category": lab["category"],
        # Comma-separated: uMap's Enum field type splits facet values on
        # "," (see Registry.Enum.parse in umap's data/fields.js), not ";".
        "application": ",".join(lab["application"]),
        "onboard_power": "yes" if lab["onboard_power"] else "no",
        "institution_type": lab["institution_type"],
        "status": lab["status"],
        "human_reviewed": "yes" if lab["human_reviewed"] else "no",
        "relevance": str(lab["relevance"]),
        "min_dim_um": str(lab["min_dim_um"]) if lab["min_dim_um"] is not None else "unknown",
    }, color


def load_polygon(lab_id: str) -> dict | None:
    path = POLYGONS_DIR / f"{lab_id}.geojson"
    if not path.exists():
        return None
    with path.open() as f:
        geometry = json.load(f)
    if geometry.get("type") not in ("Polygon", "MultiPolygon"):
        raise ValueError(f"{lab_id}: polygons/{lab_id}.geojson must be a Polygon or MultiPolygon")
    return geometry


def build_features(lab: dict) -> list[dict]:
    properties, color = build_properties(lab)
    point = {
        "type": "Feature",
        "properties": {**properties, "_umap_options": {"color": color, "iconClass": ICON_SHAPE}},
        "geometry": {"type": "Point", "coordinates": [lab["lon"], lab["lat"]]},
    }
    features = [point]

    geometry = load_polygon(lab["id"])
    if geometry is not None:
        polygon = {
            "type": "Feature",
            "properties": {**properties, "_umap_options": {"color": color, **POLYGON_OPTIONS}},
            "geometry": geometry,
        }
        features.append(polygon)

    return features


def write_geojson(category: str, labs_for_category: list) -> None:
    _, _, filename = CATEGORIES[category]
    features = []
    for lab in sorted(labs_for_category, key=lambda lab: lab["id"]):
        features.extend(build_features(lab))
    collection = {"type": "FeatureCollection", "features": features}
    with (OUT_DIR / filename).open("w") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"out/{filename}: {len(features)} features")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sort", action="store_true", help="re-sort labs.yaml by id in place and exit"
    )
    args = parser.parse_args()

    labs = load_labs()

    if args.sort:
        labs.sort(key=lambda lab: lab["id"])
        save_labs(labs)
        print(f"labs.yaml sorted ({len(labs)} entries)")
        return

    try:
        validate(labs)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if resolve_missing_coordinates(labs):
        save_labs(labs)

    OUT_DIR.mkdir(exist_ok=True)
    by_category = {category: [] for category in CATEGORIES}
    for lab in labs:
        by_category[lab["category"]].append(lab)

    for category in CATEGORIES:
        write_geojson(category, by_category[category])


if __name__ == "__main__":
    main()
