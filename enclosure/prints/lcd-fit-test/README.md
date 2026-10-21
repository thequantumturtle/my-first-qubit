# LCD fit-test prints — adult engineering use only

**Historical STL set: hold further printing pending dimensional review.**
The [1.60 mm PCB revision](../../freecad/LCD-PCB160-review.md) changes the
mounting stack and proposes smaller fasteners. These three STLs are preserved
unchanged and do not represent that revision. Replacement exports require review.

For the historical assembly, print **one of each** part below for one LCD. Test both Dorhea modules in turn;
do not start with the complete enclosure. This is an unqualified fit coupon,
not a toddler toy, load-rated part, or approval for child handling.

| STL, already oriented with lowest Z=0 | Approximate exported XYZ, mm | Bed contact |
| --- | --- | --- |
| [lcd-fit-panel.stl](lcd-fit-panel.stl) | 64 x 68 x 6.500 | Smooth front face down; posts/pockets upward |
| [lcd-lens-retainer.stl](lcd-lens-retainer.stl) | 56.999 x 45.331 x 4.000 | Flat flange rear face down; narrow nose upward |
| [lcd-rear-cradle.stl](lcd-rear-cradle.stl) | 52 x 46.926 x 3.200 | Flat rail backs down; four contact pads upward |

The panel's nominal plate is 5 mm thick; its integral 1.5 mm rear posts make the
exported maximum height 6.5 mm. STL does not encode units: import as **millimeters,
100% scale**, keeping these orientations. Do not use an inch conversion or shrink
the parts to fit the bed. No lens, LCD, fasteners, reference model, or enclosure
is included in these meshes. Full numeric checks are in [validation.json](validation.json).

Sources: [native fit test](../../freecad/MyFirstQubit_LCD_fit_test.FCStd),
[dimensioned drawing](../../freecad/LCD-fit-test-dimensions.svg),
[engineering review](../../freecad/LCD-mechanical-review.md), and
[illustrated assembly/checklist](../../../docs/lcd-fit-test-assembly.md).

## Starting print recommendations — not qualified manufacturing settings

For the first room-temperature dimensional trial, use ordinary unfilled **PLA**
on a calibrated FDM printer, consistently for all three pieces. Avoid brittle
decorative blends, abrasively filled filaments and an unvalidated coating.
PLA's low-warp, easy-print behavior makes it useful for this initial trial; it
does not establish heat resistance, impact performance or material suitability
for children. PETG is a possible later mechanical-prototype material, but requires
fresh dimensional and screw-fit checks and may string more. See the primary
[Prusa material guide](https://help.prusa3d.com/filament-material-guide) and
[PETG notes](https://help.prusa3d.com/article/petg_2059).

| Setting | Proposed starting point |
| --- | --- |
| Nozzle | 0.4 mm; calibrated extrusion width/profile |
| Layer height | 0.15 mm; first layer 0.20 mm |
| Perimeters | 4 requested; inspect thin-wall toolpaths rather than forcing four lines into a 1 mm wall |
| Solid top/bottom layers | 6 each; thin shoulders may become fully solid |
| Infill | Panel 30%; retainer/cradle 100% |
| Temperatures, cooling and speed | Start with the printer/filament manufacturer's validated PLA profile; slow small perimeters if needed |
| Raft | Off; a raft changes the front/contact finish |
| Brim | Only if needed; keep it removable without damaging bearing edges |
| Elephant foot | Calibrate; around 0.2 mm compensation is a starting experiment for a 0.4 mm nozzle, not a universal correction |

The layer recommendation is a design starting point, not a tested slicer profile.
Prusa documents layer/nozzle constraints and small-wall behavior in
[layers and perimeters](https://help.prusa3d.com/article/layers-and-perimeters_1748)
and [first-layer compensation](https://help.prusa3d.com/article/elephant-foot-compensation_114487).
No G-code or machine-specific slicing has been validated here.

## Supports and slicing inspection

- **Panel:** supports normally unnecessary in the exported front-down orientation.
  Inspect the optical lip, shallow rear pocket and blind pilots. Do not fill the
  pilots or optical opening with supports.
- **Cradle:** supports normally unnecessary with flat rails on the bed and pads
  upward. Inspect rail-to-pad joins and the small clamp walls.
- **Retainer:** its shoulder steps inward approximately 2.1 mm radially, a real
  unsupported ledge. Use localized removable support beneath this shoulder if
  the printer/profile cannot bridge it cleanly; a support-free attempt is an
  experiment requiring inspection, not a validated recommendation. Avoid support
  on the upper lens-bearing surface and in the small screw bores. Reject a
  drooping or damaged shoulder. Do not rely on slicer repair to redesign it.

Slice the three files separately or arrange them with adequate machine margins.
Their bounding rectangles, not the old screenshot layout, govern print clearance.
Check all layers around the 1 mm retainer nose wall, 0.7 mm shoulder, small pilot
bores and cradle joins. Reject disconnected islands, missing walls, warped
flanges, delamination, or slicer auto-scaling/repair warnings.

## Dimensional expectations and likely fit issues

The digital exports match the source geometry to less than 0.001 mm in overall
bounds. **That is not achievable-print accuracy or a physical measurement.** For
this trial, plan for errors on the order of +/-0.2 mm and measure the actual
printer/material result; no universal tolerance is assigned. Holes often print
undersize, first layers flare, and shrinkage/warp can exceed the small allowances.
See [Prusa's design guidance](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135).

Tight CAD allowances to check before loading the LCD:

- Retainer nose OD 38.4 into a 38.6 pocket: only **0.1 mm radial** allowance.
- Lens OD 38 into a 38.6 pocket: **0.3 mm radial** allowance; nominal axial stack
  has **zero free play**. Stock thickness and flatness matter.
- Nominal 2 mm screw through modeled 2.10 mm PCB holes: only **0.05 mm radial**
  allowance. Do not drill or enlarge the actual LCD PCB to force this design.
- Nominal 1.6 mm printed pilots and 2.4 mm bracket clearance bores need calibration.
- LCD-to-lens target 2 mm; header/panel about 0.65 mm and header/cradle about
  0.41 mm in CAD. Real solder, connectors and board thickness can consume these.

Measure a spare printed pilot and the purchased screw before tightening anything
near electronics. Do not globally scale an STL or silently drill out a trial and
record it as a nominal fit. If reworking a printed part, record the before/after
dimension and tooling; update named CAD parameters for the next controlled trial.

## Purchased parts for one fit-test station

| Item | Quantity | Status/specification |
| --- | ---: | --- |
| Existing Dorhea seven-pin GC9A01 LCD | 1 at a time | User reports model match; exact caliper dimensions not supplied |
| Clear polycarbonate disk | 1 | **Provisional diameter 38 x thickness 1.5 mm**, smooth/deburred edge; verify actual stock and cut tolerance |
| PCB/cradle screws | 2 | **Provisional M2 x 8 mm**, length measured under head; thread-forming type suitable for the selected printed plastic, not an assumed machine screw |
| Lens-retainer screws | 2 | **Provisional M2 x 4 mm**, under-head length; same pilot-fit requirement |
| Screw head limits used in CAD | — | Diameter 3.8 mm, height 1.5 mm; verify chosen drive/head geometry and actual length |
| Hand driver, calipers, good light/magnification | — | Assumed straight driver envelope diameter 4 mm x reach 10 mm; actual tool must fit |

No fastener part number is selected. Do not use ordinary M2 machine screws in
untapped plastic and assume adequate threads, or substitute a larger self-tapper.
Do not add washers or longer screws without checking stack/engagement. CAD shows
about 4.39 mm PCB screw engagement with 0.61 mm blind-bottom clearance, 2.5 mm
lens-screw engagement, and only 0.3 mm head-bearing margin at the narrow neck pads.
There is **no qualified tightening torque**. Stop if a screw binds, a pilot
cracks/strips, the board bends, or the lens is preloaded. No adhesive, solder,
charger, new battery wiring, or printed substitute lens is needed for this fit test.

## What remains unresolved before a meaningful assembly trial

Printing these calibration pieces is meaningful now. Fastened or powered testing
must wait until the actual PCB hole diameter/pitch, PCB/glass stack, clear backside
contact lands, solder/header/plug envelope, lens stock and selected screws have
been checked against the drawing. In particular, the model's **0.41148 mm PCB
thickness is not a confirmed physical reading**. If these dimensions disagree,
stop before clamping and revise the CAD; do not force the hardware.

The first trial is unpowered and adult-only. Retention, impact, repeated service,
material safety and small-part accessibility are unqualified. Record observations
using the [assembly checklist](../../../docs/lcd-fit-test-assembly.md#physical-fit-test-checklist).

## Re-exporting

Run [export_lcd_fit_test.py](../../freecad/export_lcd_fit_test.py) inside FreeCAD.
For MCP/Python console, set `MFQ_REPO_ROOT` to your checkout and execute the script
with `exec(compile(path.read_text(), str(path), 'exec'))`. The exporter reopens the
saved source, refuses a touched open source, exports only the three named solids,
normalizes each to bed Z=0, and verifies the written meshes. It never saves CAD.
Review `validation.json` and the slicer dimensions after every re-export.
