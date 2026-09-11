# microrobotics-lab-map

A curated list of microrobotics research groups, built into per-category GeoJSON
and published via git so a uMap map can render it through uMap's "Remote data"
feature. uMap has no public REST API; this pipeline exists so we never need one.
`labs.yaml` is the only thing you hand-edit.

## Setup

```
pip install pyyaml requests
```

Python >= 3.11.

## Adding a lab

Append an entry to `labs.yaml`, sorted alphabetically by `id`. Every field key
is always present (use `null` for an absent value — see the existing entries
for the shape). Two fields are worth calling out:

- `description` is the group's own public blurb and **is** rendered into the
  uMap popup.
- `notes` is your private assessment (why it's categorized the way it is, what
  to fix, etc.) and is **never** rendered or emitted anywhere in `out/` — it
  never leaves `labs.yaml`. `out/*.geojson` is published to a public repo, so
  nothing in `notes` should be written as if it might leak; it currently won't,
  but don't rely on that as your only safeguard against saying something there
  you wouldn't want public.

If you don't know the coordinates, set `lat: null` and `lon: null` — the build
geocodes from `institution, city, country` and writes the result back into
`labs.yaml`.

`osm` is a campus-outline hook (`way/<id>` or `relation/<id>` from
openstreetmap.org) — currently validated for format only. `build.py` doesn't
fetch or render the polygon yet; every entry has it `null` today. Ask for that
feature once you actually want to use it.

```
python build.py
git add labs.yaml out/ .geocode-cache.json
git commit -m "add <lab>"
git push
```

If `labs.yaml` is out of sort order, `python build.py` will refuse to run;
fix it with `python build.py --sort`.

If geocoding fails (no result, or multiple results that disagree by more than
~1 km), the build raises naming the query — fill in `lat`/`lon` by hand.

## Why `out/` is committed

`raw.githubusercontent.com` serves files from a public repo with
`Access-Control-Allow-Origin: *`, so uMap can fetch `out/*.geojson` directly
with no proxy and no server of our own. It has a short cache TTL, so a hard
reload of the map may be needed right after a push.

## labs.yaml formatting

When the build geocodes an entry and writes coordinates back, it re-serializes
the whole file with plain PyYAML (`sort_keys=False`). This does not touch
`labs.yaml` when there is nothing to geocode, but when it does run, any
hand-written YAML comments or folded (`>`) block-scalar styling will not
survive — PyYAML round-trips values, not formatting. `ruamel.yaml` would
preserve it but isn't worth the extra dependency; this is a deliberate
simplicity tradeoff.

## The map itself

This repo has no idea what uMap map (if any) it feeds — uMap has no API, so
there's nothing here to point at one. `out/*.geojson` are just public files;
any uMap map, new or existing, can be pointed at them via each layer's Remote
data settings (below). You don't need a map to exist before running
`python build.py` — it only touches `labs.yaml` and `out/`. Whether the map
itself is public/private is a separate setting in uMap's own Share dialog and
doesn't affect whether the remote-data fetch works.

## uMap wiring (one-time, per category layer)

Do this in the uMap editor. It is not automated — uMap's editing endpoints are
undocumented, session-authenticated, and out of scope by design.

1. For each category in `taxonomy.py`'s `CATEGORIES`, create a datalayer named
   after its human-readable label.
2. In that layer's settings, open **Remote data**, paste
   `https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/<category>.geojson`,
   set format to `geojson`, leave "dynamic" off (this data is static — dynamic
   refetches on every pan), leave the proxy option off.
3. Configure facet search. Current uMap (unlike some docs you may find)
   configures this through two structured dialogs, not a single `key|Label`
   text field — that shorthand is legacy and gets auto-migrated on load, but
   set it up the current way:
   - Open **Manage fields** and add one field per property you want to filter
     or search on, with the matching type:
     | Field key | Type |
     |---|---|
     | `application` | Enum (splits on `,` into multiple facet values — this is why `build.py` joins with a comma, not a semicolon) |
     | `onboard_power` | Boolean |
     | `status` | String |
     | `institution_type` | String |
     | `country` | String |
     | `relevance` | Number |
     | `min_dim_um` | String (keeps `"unknown"` as its own facet bucket instead of being dropped from a numeric range — use Number instead if you'd rather have a min/max slider and don't care about the unknown bucket) |
   - Open **Manage filters** and add a filter for each field: Checkbox widget
     for `application`, `status`, `institution_type`, `country`, `min_dim_um`;
     Switch for `onboard_power`; MinMax for `relevance`.
4. Verify the legend shows one entry per layer with the right color.

From this point the uMap map is read-only. Markers dragged in the uMap UI are
discarded on reload — that's intended; `labs.yaml` is the only source of truth.

## Popup markup

`description` uses uMap's own lightweight markup, verified against uMap's
current source (`umap/static/umap/js/modules/utils.js`, `toHTML`):
`**bold**`, `*italic*`, and `[[https://url]]` / `[[https://url|label]]` for
links. Bare `https://...` in text is auto-linked too.

One thing that is **not** true despite looking like it should be: a plain
newline is not rendered as a line break. `toHTML` has no rule that turns `\n`
into `<br>`, and no uMap popup CSS sets `white-space: pre-line`, so a
multi-paragraph `description` would otherwise collapse into one run-on
paragraph. `build.py` works around this by emitting literal `<br>` (verified
present in the popup's DOMPurify allow-list) wherever it would otherwise put a
newline.

## import_umap.py

Not used — this map is being built fresh by hand rather than migrated from an
existing uMap export, so this script was never written. If that changes, say
so and it can be added back into the plan.
