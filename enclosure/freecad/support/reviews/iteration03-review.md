# Iteration 03: calm discovery-board proposal

Adult-operated engineering prototype. Not print-ready, not child-safe, and not
for toddler handling pending mechanical, electrical, and material evaluation.
The intended observational age does not establish design qualification. The
device classically simulates a pure qubit; it is not quantum computing hardware.

## Deliverables and editable structure

- [Native FreeCAD document](MyFirstQubit_enclosure_iteration03.FCStd)
- [Complete front, top-down](iteration03-top.png)
- [Complete front, axonometric](iteration03-axonometric.png)
- [Protected LCD exploded detail](iteration03-lcd-exploded.png)
- [Generation recipe](create_iteration03.py)
- [All 55 pair clearances](iteration03-clearances.csv)
- [Geometry validation and preserved file hashes](iteration03-validation.json)
- [Measurements required before manufacture](iteration03-measurements.md)

Iterations 01 and 02 were inspected through FreeCAD MCP. Their native files
remain byte-for-byte unchanged. No firmware, hardware configuration, previous
screenshots, or earlier construction scripts were modified. No STL was exported.

The native tree contains Parameters; Housing (underlying tray/panel plus final
rounded front and rear bodies); ElectronicsPlaceholders; hidden underlying
ControlSurfaceConcepts; DiscoveryControls (nine independently editable rounded
PartDesign bodies); ProtectedDisplays (separate lenses, stepped retainers, and
active-area proxies); and hidden Construction. Native Part booleans and linked
PartDesign BaseFeatures/fillets retain dependencies. Parameters drive dimensions,
positions, rounding, and optical stack. TBD parameters are unverified envelopes
or fit assumptions. Other values are design choices, not measured hardware.
Fillet edge references can fail after large topology changes; revalidate edits.

## Comparison with iteration 02

| Element | Iteration 02 | Iteration 03 |
| --- | --- | --- |
| Footprint | 208 x 198 mm | Unchanged |
| Housing / highest point | 33.3 / 45.3 mm | 35.3 / 49.3 mm |
| Plan corner radius | 14 mm | 20 mm |
| Exterior edge rounding | Plan corners | 1.2 mm front outer rim and rear underside fillets |
| Front panel | 3 mm flat panel | 5 mm panel with internal lens pockets and front lips |
| Knobs | 40 mm cylinders | 40 x 14 mm, 6 mm top-edge rounding |
| Gates | 28 mm labeled cylinders | 28 x 6 mm, 4 mm rounded rims, no lettering |
| Measure | 40 mm bright orange | 36 x 6 mm, rounded, soft ochre |
| Reset / Colors | 22 mm labeled gray | 22 x 4 mm, cream, 2.5 mm rounded rims |
| Appearance | Technical face labels and dark surrounds | No front text or decorative graphics; warm muted palette |
| Display protection | Raised cosmetic surrounds | Separate recessed clear lenses and internal stepped rings |

Rounded taller knobs differentiate turning from pressing. The lower buttons are
rounded with broad flat centers, not fully spherical domes. A larger ochre Measure
and smaller cream secondary buttons retain hierarchy without high contrast. Gates
share size and row; subtle color and fixed position distinguish them. No small
embossed marks were added in this pass, avoiding extra visual clutter and fragile
features. Older-learner identification is provided below; a later removable adult
reference card can explain the science without dominating the face.

The specified matte appearance is a CAD material treatment, not a claim about
printed surface roughness, friction, chemical suitability, or coating durability.
Seam lines on circular controls in screenshots are CAD surface boundaries, not
grip grooves. There are no shaft bores, cap stems, or working attachment designs.

## Layout and engineering identification

XY origin is the lower-left footprint corner, +Y toward displays, +Z toward user.
All values are mm. The front is at Z=35.3; the rear underside is at Z=0.

| Function | Center X,Y | Surface diameter | Appearance / GPIO |
| --- | --- | --- | --- |
| Left / right LCD | 58,158 / 150,158 | 34 opening TBD | Shared verified SPI, independent CS/reset unchanged |
| Probability | 58,108 | 40 | Sage; encoder A/B 1/2 |
| Relative phase | 150,108 | 40 | Dusty blue; encoder A/B 41/42 |
| X | 32,65 | 28 | Sage; GPIO 5 |
| Y | 80,65 | 28 | Dusty blue; GPIO 6 |
| Z | 128,65 | 28 | Muted terracotta; GPIO 7 |
| H | 176,65 | 28 | Sage; GPIO 4 |
| Reset state | 40,28 | 22 | Cream, left; GPIO 16 |
| Measure | 104,28 | 36 | Soft ochre, center; GPIO 15 |
| Colors | 168,28 | 22 | Cream, right; GPIO 17 |

## Spacing calculated before geometry

Circle gap = center distance minus the sum of radii. The conservative LCD
envelope below includes its hidden 44 mm retainer, not only the visible aperture.

| Pair | Center distance | Envelope gap |
| --- | ---: | ---: |
| Displays | 92 | 48 (retainers) |
| Each display / knob beneath | 50 | 8 (retainer); 13 (visible aperture) |
| Knob / knob | 92 | 52 |
| Adjacent gates | 48 | 20 |
| Probability / Y; phase / Z | 48.30 | 14.30 |
| Probability / X; phase / H | 50.25 | 16.25 |
| Measure / Y or Z | 44.10 | 12.10 |
| Reset / X; Colors / H | 37.85 | 12.85 |
| Measure / Reset or Colors | 64 | 35 |

No circular-envelope overlaps. Minimum footprint-edge gaps are 18 mm for LCD
retainers, 38 mm for knobs, 18 mm for outer gates, 17 mm for secondary buttons,
and 10 mm for Measure (previously 6). These locations avoid the corner arcs;
the minima apply to the rounded outline as well as the rectangular bounds.
The footprint does not need expansion for the proposed envelopes. These are
geometric gaps, not validated finger-access or pinch-clearance requirements.

## Protected LCD stack

The exploded screenshot shows a local circular crop of the front housing, then
the transparent lens, internal stepped ring, active-area proxy, and PCB envelope.
Exploded offsets are illustrative; only the main document stores assembled
placements. The circular housing crop is a visualization, not a separate part.

| Item | Provisional dimensions / assembled height |
| --- | --- |
| Clear polycarbonate lens | Diameter 38; thickness 1.5; Z=32.8..34.3 |
| Housing viewing aperture | Diameter 34; exterior Z=35.3 |
| Front lip | 1 mm axial depth; 2 mm radial overlap over lens |
| Pocket | Diameter 38.6; 0.3 mm radial lens clearance |
| Retainer flange | OD 44 / ID 34; Z=28.3..30.3 |
| Retainer nose | OD 38.4 / ID 34; Z=30.3..32.8 |
| LCD PCB envelope | 42 x 42 x 6; Z=20.3..26.3 |
| Active-surface proxy | Diameter 34; Z=26.3..27.3 |

Lens presentation is recessed 1 mm with its outer edge concealed by the lip.
The stepped ring bears on the lens perimeter from inside; lens-to-active-surface
gap is 5.5 mm and ring-to-active-surface minimum gap is 1 mm. No adhesive or
active-surface contact is modeled. The retainer nose has just 0.1 mm radial
clearance to its pocket: this is an unresolved fit, not a manufacturing tolerance.
The nominal lens sandwich has zero axial play; a compliant interface and thermal
expansion allowance may be needed. Lens thickness drives the retainer nose height
to retain the nominal sandwich; invalid thickness/depth combinations must be
rejected during future design work. Actual LCD stack and off-axis visibility
must be measured: the 34 mm bore currently has no optical margin over the equally
provisional 34 mm active proxy. Retainer fastening and load paths remain TBD;
the geometry only demonstrates capture when the ring is secured.

## Validation, limitations, and next steps

All final components are single valid solids; all objects have valid recompute
states. No unintended volume intersections were found across housing, controls,
optical parts, electronics envelopes, and wiring reserve. Intended zero-distance
contacts include lens/lip, lens/ring, ring/panel, and active proxy/PCB. Caps and
knobs also currently sit directly on the panel: there is no validated running
clearance, travel, clearance under a pressed cap, or pinch protection. This must
be designed before functional assembly. Static CAD checks cannot establish safety.

A temporary parameter test moved the left display/knob center from 58 to 60 mm
and changed lens thickness from 1.5 to 1.7 mm; the knob moved and retainer nose
height changed from 2.5 to 2.3 mm. Values were restored before saving. Further
edits require repeating validation; the CSV/JSON reports are snapshots, not live
constraint enforcement.

The 3 mm floor/walls and 27 mm tray cavity depth are retained. A 72 x 14 x 12 mm
hidden wiring reserve is included, but does not prove harness routing, bend radii,
thermal behavior, or assembly access. USB exit, strain relief, PCB mounts,
permanent wiring, lens-retainer fasteners, and front/rear closure remain unresolved.
The separate rear tray permits conceptual disassembly; it is not a completed
serviceable closure. No front fasteners are present. No precise mounting holes
or assumed shaft interfaces were introduced.

Build volume: each main part has a 208 x 198 mm XY envelope. With a hypothetical
5 mm brim on each side this becomes 218 x 208 mm, before purge lines, clips,
keep-out zones, or machine limits. Verify actual usable printer volume. It does
not fit axis-aligned on a 200 x 200 mm bed. A nominal 220 x 220 mm machine is
tight with that brim; do not scale component fits to force a smaller bed. If
necessary, engineer and validate a split part/joint or use a larger printer.

Next: measure actual electronics and lens stock; resolve the optical stack and
internal ring fastening; design positive control retention, moving clearances,
and PCB load supports; design rear-only service fasteners and cable management;
then make adult bench fit coupons and run the existing functional test plan.
Separate material, mechanical, electrical, impact, retention, and child-safety
reviews precede any toddler access. Appearance does not establish suitability.

Discovery mode is future work. Firmware is unchanged: current animations can
continue after an input ends, brief button presses during them can be missed,
and existing palettes/technical display labels remain. The CAD previews' plain
colored disks are static placeholders, not a firmware change or a promise of
immediate/stops-on-release behavior. All seven scientific functions remain
mapped to their existing inputs underneath the simplified physical face.
