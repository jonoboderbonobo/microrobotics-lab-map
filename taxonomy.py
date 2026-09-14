"""Category scheme for the microrobotics lab map.

The axis is CONTRIBUTION TYPE: how a group can plausibly contribute to a
microrobotics effort. It is deliberately not a research-field taxonomy and not
an institution-type taxonomy. Institution type, application domain, scale and
contact status are separate axes and live as GeoJSON properties consumed by
uMap's facet search -- never as colors.

One category per entry, exactly. Each category maps to (label, color, filename):
the color is a CSS color name that uMap accepts directly, and the filename is
the GeoJSON file that becomes one uMap datalayer.

Rationale per category, so the scheme does not drift:

micro-robotics
    Labs that build the WHOLE robot as a system -- not just a sensor or an
    actuator -- and whose autonomous unit is under 1 mm in every dimension.
    Externally actuated particles do not qualify: if the magnets, the sensors
    and the computer are counted, those are meter-scale robots. This category
    is genuinely small.

    Actually enforced (2026-09): re-audited every prior micro-robotics entry
    against this rule specifically, since the category had accumulated many
    externally-actuated systems the literature calls "microrobots" but which
    don't carry their own actuation/energy/memory. Confirmed genuinely
    autonomous as of this audit: cornell-cohen, cornell-mceuen, tuc-schmidt,
    upenn-miskin, westlake-wang -- all onboard-photovoltaic-or-equivalent,
    onboard-actuation whole systems. Two more (harvard-microrobotics /
    RoboBee, mit-smrl) are *aiming* at power autonomy but, per their own PIs'
    public statements, aren't there yet (still tethered/beamed power) --
    filed under micro-nano-end-effectors until that changes, not here on the
    strength of the goal alone.

micro-nano-end-effectors
    Externally-actuated micro/nanoscale tools, particles, grippers, and
    swimmers -- magnetic, acoustic, optical, or chemically self-propelled --
    that the literature very commonly calls "microrobots" or "nanorobots"
    but which do not carry their own actuation, energy, or memory onboard.
    This is most of what search turns up under that term; the category
    exists specifically to stop that literature conflation from collapsing
    into the strict `micro-robotics` bucket above. Includes nanoparticle-
    based systems (drug-carrying particles, catalytic Janus motors) under
    the same logic -- a nanoparticle steered/propelled externally is the
    same kind of thing as a magnetically-steered microgripper, just smaller.

biohybrid-robotics
    Robots whose actuating body is (or is derived from) a living organism or
    genetically/chemically modified living cells -- magnetotactic bacteria,
    engineered immune cells, sperm cells, algae -- rather than a wholly
    synthetic structure. Kept separate from micro-nano-end-effectors even
    though most current examples are also externally steered (e.g.
    magnetically), because the biological-chassis angle is a distinct axis
    from actuation method: a synthetic magnetic microgripper and a
    magnetically-steered living-sperm-cell carrier raise very different
    fabrication, biocompatibility, and ethical questions despite both being
    externally driven.

milli-robotics
    Millimeter- and centimeter-scale autonomous robots. Forces and fabrication
    differ completely from microscale, but communication, path planning and
    control problems are shared. Candidates to be pulled down in scale if a
    good microrobotics framework exists.

electronic-engineering
    Chip design for microrobotics, smart dust, or very small autonomous
    implants. High value because most chip designers have no interest in the
    topic while good ones -- especially analog -- are expensive and scarce.

material-lab
    Arguably most self-described "microrobotics labs". They produce
    transducers, actuators, particles and other cleanroom output that is
    useful to microrobotics without being a robot. Worth mapping when they at
    least intend their output to end up in an actual microrobot.

neuroscience-lab
    Faces closely analogous chip-design constraints for implants and
    measurement -- not locomotion, but the same power, size and interface
    problems. Also applied surgery with externally controlled particles, which
    is less interesting in itself but is a contact point with the community.

information-technology
    Path planning, efficient algorithms, neuromorphic computing, swarm
    behavior. These are what let a microrobot get smaller while remaining an
    actual robot rather than a particle.

biomedical-lab
    Two distinct sub-interests: microrobots grown or gene-manipulated from
    living cells, and -- more useful -- biomedical applications such as
    individualized therapy and drug delivery. Likely best customers, and a
    source of concrete problem statements to design against.

nano-medicine
    Assumed to sit closer to application than biomedical labs, therefore
    closer to being customers rather than joint-research partners. The
    distinction from biomedicine is not sharp; the people in those camps treat
    it as meaningful, which is reason enough to keep the split. Covers both
    labs and companies.

medicine-lab
    Macroscopic medicine. Different problems and different expectations of a
    microrobot than the nano/biomedical camps. Joint research, customers, and
    statements of need.

hospital
    Hospitals and clinicians willing to deploy experimental microrobotics.
    Critical for clinical trials and publicity. Customers, or customers of
    customers. Their problems should be the problems being solved.

cleanroom-service
    Fabs and foundries that sell cleanroom/fabrication capacity as a service
    (e.g. MPW runs) rather than running their own research program. Distinct
    from material-lab: a material-lab's output is its own research; a
    cleanroom service's output is fabrication capacity for someone else's
    design. High value for actually getting a design made.
"""

CATEGORIES = {
    "micro-robotics":        ("Micro-Robotics Lab",             "DarkBlue",       "micro-robotics.geojson"),
    "micro-nano-end-effectors": ("Micro/Nano End-Effector",     "Indigo",         "micro-nano-end-effectors.geojson"),
    "biohybrid-robotics":    ("Biohybrid Robot",                "SaddleBrown",    "biohybrid-robotics.geojson"),
    "milli-robotics":        ("Milli-Robotics Lab",             "RoyalBlue",      "milli-robotics.geojson"),
    "electronic-engineering": ("Electronic Engineering (Chip) Lab", "White",      "electronic-engineering.geojson"),
    "material-lab":          ("Material Lab",                   "DarkViolet",     "material-lab.geojson"),
    "neuroscience-lab":      ("Neuroscience Lab",               "DarkOrange",     "neuroscience-lab.geojson"),
    "information-technology": ("Information Technology",        "DarkCyan",       "information-technology.geojson"),
    "biomedical-lab":        ("Biomedical Lab",                 "DarkGreen",      "biomedical-lab.geojson"),
    "nano-medicine":         ("Nano-Medicine",                  "MediumSeaGreen", "nano-medicine.geojson"),
    "medicine-lab":          ("Medicine Lab",                   "DarkOliveGreen", "medicine-lab.geojson"),
    "hospital":              ("Hospital",                       "Crimson",        "hospital.geojson"),
    "cleanroom-service":     ("Clean Room Service",             "SlateGray",      "cleanroom-service.geojson"),
}

# Marker shape. Uniform across categories -- color carries the category, shape
# is not a second encoding of the same thing.
ICON_SHAPE = "Ball"

# Polygon styling, applied to every campus outline. Same color as the marker,
# inherited fill.
POLYGON_OPTIONS = {
    "opacity": 0.5,
    "weight": 3.5,
    "fillOpacity": 0.3,
}

APPLICATIONS = {"medical", "environmental", "industrial", "fundamental"}
INSTITUTION_TYPES = {"university", "institute", "hospital", "company"}
STATUSES = {"watch", "contacted", "collaborating"}

"""
Example:

https://github.com/jonoboderbonobo/microrobotics-lab-map


https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/micro-robotics.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/milli-robotics.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/electronic-engineering.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/material-lab.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/neuroscience-lab.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/information-technology.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/biomedical-lab.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/nano-medicine.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/medicine-lab.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/hospital.geojson
https://raw.githubusercontent.com/jonoboderbonobo/microrobotics-lab-map/main/out/cleanroom-service.geojson
"""

