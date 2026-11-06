# Iteration 03 candidate LCD integration

This new branch of the CAD study is based on **Iteration 03**, not the thicker
V0.4 battery packaging proposal. Neither source design was overwritten. Future
consolidation must bring measured LCD geometry into the battery revision after
component verification; this study does not remove the battery architecture
requirement.

- [Native enclosure assembly](MyFirstQubit_iteration03_candidate_LCD.FCStd)
- [Positioned modules, rear axonometric](iteration03-candidate-LCD-inside.png)
- [Positioned modules, straight rear view](iteration03-candidate-LCD-rear.png)
- [Full clearance results and protected hashes](iteration03-candidate-LCD-clearances.json)
- [Component, dimensional comparison and measurements](../../hardware/models/gc9a01-meta-mcu/README.md)
- [Import/integration recipe](import_candidate_gc9a01.py)

## Assembly and alignment

Two external App::Links reference the separate native component document under
`hardware/models/gc9a01-meta-mcu/`. Both links are clearly labeled **Dorhea fit
UNVERIFIED**. Each contains the candidate PCB, seven-contact connector and LCD
body; they are not independent duplicated geometry. Keep that component file
with the assembly when moving the project and ensure FreeCAD resolves its links.

Existing panel centers remain (58,158) and (150,158) mm. The component datum is
the modeled LCD disk axis, not the PCB-circle center. Its front plane is placed
at Z=27.3 mm, matching the former I03 active-surface proxy. This depth is a
provisional placement choice, not a measured Dorhea glass location. The two
links' positions are driven by the existing Parameters sheet; the new
CandidateLCDParameters sheet holds the front-plane depth and added connector
reserve. No front, mounting or wiring geometry was changed.

The new revision hides and labels the four superseded LCD board/active proxies.
The import component retains the original STEP hierarchy and normalized copies.
The PCB and glass are source BRep geometry, not parametric fabrication models.
All imported final solids are valid, and no assembly object has an invalid
recompute state. Prior .FCStd files are checksum-preserved in the validation log.

The screenshots hide the rear tray and reveal the interior against the front
panel. Other green volumes are unmeasured ESP32, breadboard, encoder, switch and
wiring placeholders; they are not verified internals. The straight rear view
reverses the visual upper/lower orientation relative to the front view.

## Clearance results at the provisional depth

Both sides have the same nominal placement and nearest clearances:

| Pair | Minimum surface distance mm |
| --- | ---: |
| Modeled LCD front/body to polycarbonate lens | 5.50 |
| LCD body to internal lens retainer | 1.00 |
| PCB to lens retainer | 3.00 |
| Connector to front housing | 1.95 |
| Connector to lens retainer | 2.11 |
| Connector to probability/phase encoder envelope | 15.27 |
| PCB to ESP32 envelope | 12.97 |
| Rear of modeled connector to original tray floor | 13.50 |

No candidate PCB/header/LCD volume intersections with the enclosure, lens,
retainer, controls or other electronics placeholders were found. No conflicts
were found for a further **6 mm axial connector/wiring reserve** behind each
modeled connector; that reserve uses only the source connector's XY footprint
and is NOT a measured mating plug or a complete wire-bend envelope. Broader
plugs, wires, solder and assembly sweeps still require measurement. Intrinsic
upstream PCB/header overlap is separately documented in the component README.

The modeled body is 35.2 mm diameter behind a 34 mm optical opening. That body
is not the active area, so the CAD cannot establish unobstructed pixels. A
1.28-inch marketing size is insufficient to determine the physical glass/active
area, its position or viewing cone. Confirm the actual active diameter and
center, off-axis visibility and lens spacing on the Dorhea boards before
changing the aperture or fabricating supports. The current 1 mm retainer gap
also needs a full tolerance/deformation budget and a valid fastening design.

Passing these static checks establishes only the feasibility of this candidate
placement. It does not establish Dorhea fit, contact-free behavior under load,
thermal clearance, reliable wiring, control retention, secure enclosure service
access or child safety. No mounting bosses or precision holes, firmware edits,
STL exports, commits or pushes are included.
