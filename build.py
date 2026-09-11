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
from taxonomy import PARADIGMS
from validate import validate

ROOT = Path(__file__).parent
LABS_PATH = ROOT / "labs.yaml"
OUT_DIR = ROOT / "out"


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


def build_description(lab: dict, paradigm_label: str) -> str:
    header = f"**{lab['pi']}**" if lab["pi"] else f"**{lab['name']}**"
    header += f" — {lab['institution']}, {lab['city']} ({lab['country']})"
    lines = [header]

    if lab.get("notes"):
        lines += ["", lab["notes"].strip()]

    links = [f"[[{lab['url']}|Group website]]"]
    if lab.get("people_url"):
        links.append(f"[[{lab['people_url']}|People]]")
    lines += ["", *links]

    min_dim = f"{lab['min_dim_um']} µm" if lab["min_dim_um"] is not None else "unknown"
    lines += ["", f"Paradigm: {paradigm_label} · Smallest demonstrated: {min_dim}"]

    return "\n".join(lines)


def build_feature(lab: dict) -> dict:
    paradigm_label, color, _ = PARADIGMS[lab["paradigm"]]
    properties = {
        "name": lab["name"],
        "description": build_description(lab, paradigm_label),
        "id": lab["id"],
        "pi": lab["pi"] or "",
        "institution": lab["institution"],
        "country": lab["country"],
        "paradigm": lab["paradigm"],
        # Comma-separated: uMap's Enum field type splits facet values on
        # "," (see Registry.Enum.parse in umap's data/fields.js), not ";".
        "application": ",".join(lab["application"]),
        "onboard_power": "yes" if lab["onboard_power"] else "no",
        "institution_type": lab["institution_type"],
        "status": lab["status"],
        "relevance": str(lab["relevance"]),
        "min_dim_um": str(lab["min_dim_um"]) if lab["min_dim_um"] is not None else "unknown",
        "_umap_options": {"color": color, "iconClass": "Drop"},
    }
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": {"type": "Point", "coordinates": [lab["lon"], lab["lat"]]},
    }


def write_geojson(paradigm: str, labs_for_paradigm: list) -> None:
    _, _, filename = PARADIGMS[paradigm]
    features = [build_feature(lab) for lab in sorted(labs_for_paradigm, key=lambda lab: lab["id"])]
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
    by_paradigm = {paradigm: [] for paradigm in PARADIGMS}
    for lab in labs:
        by_paradigm[lab["paradigm"]].append(lab)

    for paradigm in PARADIGMS:
        write_geojson(paradigm, by_paradigm[paradigm])


if __name__ == "__main__":
    main()
