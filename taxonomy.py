"""Single source of truth for the paradigm taxonomy.

The axis is actuation and autonomy paradigm -- not research field, not
institution type. Application domain, institution type, scale, and contact
status are separate axes; they live as GeoJSON properties for uMap's facet
search, never as colors. Do not add other axes here.

Each entry: paradigm slug -> (human-readable label, CSS color name, output filename).
"""

PARADIGMS = {
    "external-field": ("External field actuation", "Blue", "external-field.geojson"),
    "wave-driven": ("Acoustic / optical / chemical", "Cyan", "wave-driven.geojson"),
    "biohybrid": ("Bio-hybrid", "Green", "biohybrid.geojson"),
    "mems-actuation": ("MEMS actuators & fabrication", "Purple", "mems-actuation.geojson"),
    "autonomous": ("Onboard power / autonomous", "Orange", "autonomous.geojson"),
    "tooling": ("Assembly, manipulation, metrology", "Gray", "tooling.geojson"),
}

APPLICATIONS = {"medical", "environmental", "industrial", "fundamental"}

INSTITUTION_TYPES = {"university", "institute", "hospital", "company"}

STATUSES = {"watch", "contacted", "collaborating"}
