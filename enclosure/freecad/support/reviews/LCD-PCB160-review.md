# LCD dimensional correction: provisional 1.60 mm PCB

October 21, 2026. Adult-operated engineering study; not a manufacturing release.
This revision supersedes the earlier stack assumptions for further design review.
All previous native models, vendor files and three exported STLs are preserved.

## Evidence and comparison

The additional compatible-module drawing was **not available locally**. The
dimensions below were transcribed by the user; its manufacturer, revision,
datums, tolerances beyond those listed, and the 11.3 mm annotation could not be
independently inspected. No new drawing image has been invented or attributed.
Earlier user-reported visual/physical agreement with the META-MCU model does
not constitute numerical measurement of these Dorhea units. **No dimensions
in this comparison are physically verified Dorhea measurements.**

| Dimension, mm | Original STEP-derived reference | New working reference | Evidence / qualification |
| --- | --- | --- | --- |
| PCB thickness | 0.41148 | 1.60 | Compatible drawing; provisional |
| Overall PCB width | 38.1532 | 38 | Compatible drawing; provisional |
| Overall PCB length | 44.6532 | 45.5 | Compatible drawing; provisional |
| LCD outer width/diameter | 35.2 | 35.6 nominal | Drawing ±0.1; cylinder approximation |
| LCD assembly thickness | 1.5 | 1.50 | Drawing ±0.1; simplified body, not FPC/bezel detail |
| Active diameter | Not modeled | 32.4 | Drawing; documented parameter, not a separate solid |
| Hole diameter | 2.10000 | 2.0 | Drawing; actual usable hole size unknown |
| Hole pitch | 23.0000 | 23 nominal | Drawing says approximately 23; STEP axes retained |
| Rear SMD height | Not modeled | 1.2 maximum | Drawing; blanket envelope except contact lands/header |
| Seven connection pitch | 2.54 | 2.54 | STEP and supplied drawing agree nominally |
| 11.3 annotation | No reliable correspondence | **Unassigned** | Cannot establish axis/endpoints without drawing |

The STEP itself contains `SI_UNIT(.MILLI.,.METRE.)` and explicit board coordinates
at 0.41148 mm (including entities #16 and #44). FreeCAD's analytical BRep bounds
agree. This is not a global import scaling error: other dimensions, including
2.54 mm connector pitch, are plausible at millimeter scale. Why the source
author used that PCB thickness remains unknown; no conversion-factor diagnosis
or original design intent is asserted.

## Native documents and construction

- [Revised component](../../hardware/models/gc9a01-meta-mcu/GC9A01_drawing_PCB160_provisional.FCStd)
- [Revised enclosure assembly](MyFirstQubit_iteration03_LCD_PCB160.FCStd)
- [Revised independent fit test](MyFirstQubit_LCD_fit_test_PCB160.FCStd)
- [Construction and validation recipe](create_lcd_pcb160_revision.py)
- [Shared-datum, fit-assembly and final reopen checks](validate_lcd_pcb160_revision.py)
- [Geometry validation](LCD-PCB160-validation.json)
- [Dimensioned stack comparison](LCD-PCB160-section-dimensions.svg)
- [CAD cross-section](LCD-mount-section-PCB160.png)
- [Exploded assembly](LCD-mount-exploded-PCB160.png)
- [Installed assembly](LCD-mechanical-inside-PCB160.png)
- [Fit assembly](LCD-fit-test-assembled-PCB160.png)

The new component uses native cylinders/box/fuse/cut features controlled by
`DrawingParameters`. Its outline is a provisional 38 mm circular board with
28.5 mm neck, extended to 45.5 mm overall. Neck width, outline center offsets,
hole-axis coordinates and header remain STEP-derived working assumptions.
The original fine outline details are not claimed to be reproduced. In
particular, the new drawing does not establish the LCD-to-board center offset
or hole-to-board-edge distances. Do not drill or manufacture from these datums.
The unchanged STEP header is retained as a separate provisional reference;
the 11.3 mm callout has not been mapped onto it.

Each assembly uses two external links to the new component; the fit test uses
one. PCB thickness in both mounting sheets references the component spreadsheet.
Optical, positioning and mount dimensions remain editable named parameters.
Legacy `M2...` spreadsheet aliases now hold **M1.6 candidate envelope** dimensions
for compatibility with the shared historical construction functions; labels and
this report identify the proposed size. These are not purchased screw specs.

## Stack and mounting consequences

Global +Z faces the user. Full enclosure panel underside/top remain Z30.3/35.3.
The optical front remains **Z30.8**, lens rear/front Z32.8/34.3, giving the same
**2.0 mm nominal air gap** and 1.5 mm polycarbonate thickness.
PCB front remains Z28.8000015: the old approximately 0.5 mm LCD-rear-to-PCB-front
stand-off is retained as an explicitly unverified STEP assumption. Therefore
the posts stay approximately **1.5 mm** high; thickness grows rearward.

| Stack, mm | Previous | Revised |
| --- | --- | --- |
| PCB back Z | 28.3885215 | 27.2000015 |
| Rear component clearance from PCB back to cradle base | 1.2 | 1.6 (1.2 SMD + 0.4 margin) |
| Cradle base front Z | 27.1885215 | 25.6000015 |
| Cradle base rear Z | 25.1885215 | 23.6000015 |
| Cradle total thickness, including contact pads | 3.2 | 3.6 |
| Nominal engagement of proposed 8 mm PCB screw | 4.38852 | 2.8 |
| Screw tip to 5 mm blind-pilot end | 0.61148 | 2.2 |
| Roof above PCB pilot end | 1.5 | 1.5 |
| Lens screw nominal engagement, 4 mm candidate | 2.5 | 2.5 |

The cradle moves **1.58852 mm rearward**. Footprint remains 208 × 198 mm;
no increase in enclosure thickness is required by this LCD-only study. The
separate battery proposal is still not consolidated into this assembly.

Drawing holes of 2.0 mm give zero nominal diametral clearance for M2 screws.
This revision instead explores 1.6 mm shanks, provisional 3.2 × 1.3 mm heads,
8 mm PCB and 4 mm ring lengths, with provisional 1.2 mm blind pilots and
existing 2.4 mm printed clearance bores. Nominal radial PCB-hole clearance is
0.2 mm. Fastener type, real dimensions, suitable pilot, required engagement,
pullout resistance and torque must be selected/tested; 2.8 mm engagement is a
geometric calculation, not strength qualification. No threads are simulated.

The rear SMD/solder reserve is 1.2 mm across the board except four deliberate
support lands and the header area. These exclusions are **not verified clear
lands**: verify components, tracks, insulation and load paths before clamping.
Seven separate 1 mm diameter × 2 mm rear pin envelopes are conservative design
placeholders, not measured pin lengths. A separate 20 × 8 × 8 mm harness
envelope supplements the existing STEP-header/mating reserve. Their dimensions,
position, wire bend/insertion/removal sweep and solder protrusions need actual
measurement. Envelope overlap with its own header/PCB is intentional.

## Validation and limitations

See the JSON for actual results, pairwise clearances and protected-file hashes.
Checks cover valid solids, unintended volume intersections, component-to-panel,
ring/cradle/lens/rear-tray clearances, SMD and header reserves, added pin/wiring
reserves, controls and ESP32/breadboard placeholders. Surface contact at support
lands is intentional. PCB and cradle geometry must not be mistaken for fully
populated board scans. The 35.6 mm LCD body has nominal 0.4 mm radial clearance
inside the 36.4 mm ring bore; +0.1 mm diameter reduces this to 0.35 mm before
printing/alignment errors. A centered 32.4 mm active circle has 0.8 mm radial
margin in the 34 mm aperture; viewing angle and real centering remain untested.

All new documents are reopened from disk. PCB thickness is perturbed +0.1 mm
to check cradle movement and shared component-to-mount propagation, then restored.
Earlier source/STL/firmware/wiring hashes are checked after creation. Lens-ring
driver access still requires removing cradle and LCD first; this service-order
constraint is not a new collision. No replacement meshes are exported.

## Before another print

**Recommend superseding the original three-STL set after this revision is
reviewed and replacement exports are separately authorized.** Preserve it as
historical output; do not use its 0.41148 mm/M2 stack for the next fit decision.
The thicker cradle and changed pilot/fastener proposal require a coordinated
set and revised manufacturing instructions, even where a part is unchanged.

Obtain the original compatible drawing and resolve its 11.3 mm datums. Measure
both actual boards: PCB thickness/outline, hole diameter/pitch/coordinates,
LCD front-to-PCB stack, FPC/bezel, rear component heights and safe support lands,
solder/pin/plug envelope and harness routing. Verify actual polycarbonate stock,
cut diameter/flatness/edge finish, lens gap under loads, active area centering,
selected fasteners and driver access. Then test print dimensions, assembly,
stress-free support and service sequence before powered operation.

Mechanical retention, impact resistance, electrical/material safety and small
component accessibility remain unresolved. This is not child-safe or ready for
manufacturing.
