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

For a campus outline, save its geometry as `polygons/<id>.geojson` — a bare
GeoJSON `Polygon`/`MultiPolygon` geometry object, no properties, no `Feature`
wrapper (see any existing file in `polygons/` for the shape). `build.py`
picks it up by filename automatically and emits it as a second feature
alongside the point marker, styled via `taxonomy.py`'s `POLYGON_OPTIONS` plus
the category color. No `labs.yaml` field needed for this.

`osm` (`way/<id>` / `relation/<id>` from openstreetmap.org) is a *different*,
not-yet-built mechanism reserved for live-fetching a polygon from OSM by id at
build time — currently validated for format only, always `null`. The
`polygons/` files are hand-sourced instead (from the original hand-drawn
map's already-verified shapes, in the initial migration).

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
   set it up the current way. This is done **once, at the map level** (not
   per layer — verified in uMap's own source, `app.js`: the map object owns
   its own `fields`/`filters` collections, separate from any one layer's),
   so you don't repeat it 11 times:
   - The whole panel only exists when the map's edit mode is **Advanced** —
     if you open the map's settings/edit panel and don't see a "Manage
     Fields" section at all, that's why; find the simple/advanced edit-mode
     toggle in the map's general settings and switch it first.
   - With Advanced mode on, click the map's **Edit** control (gear icon) to
     open "Map advanced properties", then find the **Manage Fields** section
     (a collapsible panel partway down). Click **Add a new field** once per
     property you want to filter or search on, with the matching type:
     | Field key | Type |
     |---|---|
     | `application` | Enum (splits on `,` into multiple facet values — this is why `build.py` joins with a comma, not a semicolon) |
     | `onboard_power` | Boolean |
     | `status` | String |
     | `institution_type` | String |
     | `country` | String |
     | `relevance` | Number |
     | `min_dim_um` | String (keeps `"unknown"` as its own facet bucket instead of being dropped from a numeric range — use Number instead if you'd rather have a min/max slider and don't care about the unknown bucket) |
   - Adding a field only makes it *available*; it doesn't put a widget in
     the sidebar yet. Still inside Fields management, click **Manage
     filters** and **Add filter** once per field you actually want visible
     and interactive: Checkbox widget for `application`, `status`,
     `institution_type`, `country`, `min_dim_um`; Switch for
     `onboard_power`; MinMax for `relevance`. Give each one a human-readable
     label (e.g. "Onboard power") — that's what shows in the sidebar, not
     the raw field key.
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

Used once to migrate the old hand-drawn map (38 new labs added, plus campus
polygons for those and the 6 already-hand-curated entries into `polygons/`),
then deleted per its own design intent — it's one-time migration code, not
part of the ongoing pipeline. Recoverable from git history if ever needed
again.

Every migrated entry got real defaults for the fields the export can't know,
rather than build-blocking placeholders: `status: watch`, `relevance: 1`,
`application: []`, `onboard_power: false`. `institution_type` was set from
general knowledge of each institution (a verifiable fact, unlike the others),
not left generic. None of this is asserted as correct — each entry's `notes`
spells out exactly what was defaulted and needs a real look, in plain text
rather than as something that blocks the build. `relevance` in particular is
almost certainly wrong for every one of the 38 (it's set uniformly to the
floor, 1, because it's entirely your subjective call and there's no honest
way to guess it) — go through and actually score these when you get a chance.

The old map also had ten single-person placeholder-pin layers (one map layer
per named researcher, e.g. "Metin Sitti - Stuttgart/Istanbul") plus an empty
"Individuals" layer. All ten were dropped: every one of those pins was a bare
marker with no name or description at all, and every person they represented
already had a full entry in one of the category layers. Nothing here
recreates that one-layer-per-person pattern — an individual researcher is
just a normal `labs.yaml` entry with `pi` set, findable via uMap's built-in
search box across whatever category they're filed under, which is what "one
layer for all individuals, filtered by name" comes down to in this design.
