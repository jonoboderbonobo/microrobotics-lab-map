# microrobotics-lab-map

A curated list of microrobotics research groups, built into per-category GeoJSON
and published via git so an existing uMap map can render it through uMap's
"Remote data" feature. uMap has no public REST API; this pipeline exists so we
never need one. `labs.yaml` is the only thing you hand-edit.

## Setup

```
pip install pyyaml requests
```

Python >= 3.11.

## Adding a lab

Append an entry to `labs.yaml` (see the field table in the project brief), sorted
alphabetically by `id`. If you don't know the coordinates, set `lat: null` and
`lon: null` — the build will geocode it from `institution, city, country` and
write the resolved value back into `labs.yaml`.

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
hand-written YAML comments or folded (`>`) block-scalar styling in `notes`
fields will not survive — PyYAML round-trips values, not formatting.
`ruamel.yaml` would preserve it but isn't worth the extra dependency; this is
a deliberate simplicity tradeoff.

## uMap wiring (one-time, per paradigm layer)

Do this in the uMap editor. It is not automated — uMap's editing endpoints are
undocumented, session-authenticated, and out of scope by design.

1. For each paradigm in `taxonomy.py`, create a datalayer named after its
   human-readable label.
2. In that layer's settings, open **Remote data**, paste
   `https://raw.githubusercontent.com/<user>/<repo>/main/out/<paradigm>.geojson`,
   set format to `geojson`, leave "dynamic" off (this data is static — dynamic
   refetches on every pan), leave the proxy option off.
3. Delete the old hand-drawn layers once the new ones render correctly.
4. Configure facet search. **Note:** current uMap (unlike older docs you may
   find) configures this through two structured dialogs, not a single
   `key|Label` text field — that shorthand is legacy and gets auto-migrated on
   load, but set it up the current way:
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
5. Verify the legend shows one entry per layer with the right color.

From this point the uMap map is read-only. Markers dragged in the uMap UI are
discarded on reload — that's intended; `labs.yaml` is the only source of truth.

## Popup markup

`description` uses uMap's own lightweight markup, verified against uMap's
current source (`umap/static/umap/js/modules/utils.js`, `toHTML`):
`**bold**`, `*italic*`, and `[[https://url]]` / `[[https://url|label]]` for
links. Bare `https://...` in text is auto-linked too.

## import_umap.py

Not written yet — deferred until there's an existing uMap export to migrate
from. Once it's used for the one-time migration, delete it; it is not part of
the ongoing pipeline.
