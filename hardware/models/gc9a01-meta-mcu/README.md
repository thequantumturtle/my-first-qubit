# GC9A01 candidate component: Dorhea match NOT verified

This is a detailed reference imported from META-MCU, not a measured model of our
two Dorhea boards. Identical controller, nominal screen size and pin count do not
establish mechanical interchangeability. Do not design Dorhea precision mounts
from this component until both physical boards are checked.

Files: [original STEP](source/frame_size.step), [drawing](source/frame_size.jpg),
[native component](GC9A01_META_MCU_candidate.FCStd),
[component preview](candidate-component.png),
[dimensional data](dimensional-findings.json), and [license/attribution](NOTICE.md).

## Source versus imported geometry

The upstream README describes 1.28 inch, 240x240 RGB, 3.3 V, four-line SPI and a
seven-pin connector. Its prose size of 28.5 x 44.5 mm uses the neck width rather
than the complete upper outline: the drawing explicitly labels a 38 mm upper
diameter and 28.5 mm neck width. The drawing's display/PCB-circle reference is
(14.25,25.5) from the neck's lower-left origin; another internal reference at
(14.25,15.5) is not a separate mounting feature. No dimensioned side view or
complete optical/connector tolerance specification is supplied in that drawing.

| Feature | Drawing / README | STEP geometry measured in FreeCAD |
| --- | --- | --- |
| Upper board diameter / total width | 38 mm | Circular outline diameter 38.1532 mm; full width 38.1532 mm |
| Neck width | 28.5 mm | Nominal neck corners near X=0 and 28.5, with small edge rounds |
| Full board height | README 44.5 mm | 44.6532 mm analytic bounding height |
| Board thickness | Not stated | 0.41148 mm; must not be treated as actual Dorhea thickness |
| Board circle center | 14.25,25.5 mm | 14.249999,25.500000 mm |
| Simplified LCD disk | Nominal screen 1.28 inch; no active-area dimension | Cylinder diameter 35.2000; thickness 1.5000 mm |
| Modeled disk center | Not separately specified | 13.970006,25.781002 mm |
| Disk top / board top (source Z) | Not stated | 1.999999 / 0 mm |
| Two mounting holes | Diameter 2 mm | Diameter 2.100001 mm |
| Mount-hole centers | Not fully dimensioned | (2.7500,2.0550), (25.7500,2.0550); 23 mm apart |
| Seven contact holes | Seven signal names | Diameter 0.9000; 2.54 mm pitch; row Y=1.3250 |
| Contact X centers | Not dimensioned | 6.63,9.17,11.71,14.25,16.79,19.33,21.87 mm |
| Connector modeled envelope | Not dimensioned | 17.7800 x 2.5400 x 11.8500 mm |
| Complete modeled Z range | Not dimensioned | -8.8000..3.0500 mm, dominated by the connector |

Measurements use analytic cleaned BReps, not cached display triangulation.
The imported cache reports only 38.1194 x 44.5845 mm for the board and a slightly
undersized disk bounding box. Removing the cache changes measurement bounds,
not geometry. Values above describe the digital reference; extra decimal places
do not imply manufacturing precision. Model tolerances and source discrepancies
rule out using these values as verified Dorhea fit data.

The PCB is round above a narrower connector neck, with two holes flanking the
seven contacts. The connector has seven detailed turned-contact bodies/pins and
an unusual full-height envelope; it is not a confirmed match to the soldered
header on the physical Dorhea boards. There are only three source solids: PCB,
connector and simplified LCD cylinder. Rear electronic parts, FPC, adhesive,
glass/bezel detail, solder fillets, silkscreen and active display area are absent.
The STEP contains about 0.420 mm^3 of intrinsic PCB/connector overlap; this is
retained as upstream geometry, not silently repaired or counted as an enclosure
collision. The three solids individually pass FreeCAD validity checks.

The disk axis differs from the PCB-circle datum by (-0.279994,+0.281002) mm,
approximately 0.397 mm radially. No evidence resolves whether that offset is
intentional or a source modeling error. The disk is not the active pixel area;
do not use its 35.2 mm diameter to assert the display has a larger active screen.

## Comparison with our Dorhea specification

| Attribute | Project evidence for Dorhea | Candidate comparison |
| --- | --- | --- |
| Brand/model | Dorhea 1.28-inch GC9A01 7-pin SPI module | META-MCU reference, not Dorhea-branded |
| Resolution/controller | 240x240, GC9A01 | Same stated resolution/controller |
| Power used on bench | 3.3 V; 5 V tolerance not assumed | README specifies 3.3 V |
| Signal functions | VCC,GND,SCK/SCL,MOSI/SDA,DC,CS,RST | Same functions, but ordered GND,VCC,SCK,SDA,RST,DC,CS in candidate drawing |
| Physical pin order | Not recorded as a position-specific Dorhea specification | NOT verified; follow actual silkscreen, not candidate pin positions |
| PCB outline, thickness, holes, LCD stack and header | No verified dimensions or exact product drawing in repository | Cannot establish a mechanical match |

An additional search did not establish an authoritative drawing tied to our
specific purchased Dorhea boards. Dimensions of other GC9A01 vendors were not
substituted for Dorhea measurements. Electrical function overlap is useful
context but does not authorize rewiring or changing the verified supply.

## Component datum and assembly use

The native file retains the original imported `PCB` hierarchy, hidden, plus
`CandidateModule` containing separately inspectable PCB, connector and LCD BReps.
Origin is at the imported LCD disk axis on its front face, +Z toward the viewer,
and the header lies toward -Y. The transform subtracts source datum
(13.970006,25.781002,1.999999) mm; no scaling or geometry correction is applied.

The [new Iteration 03 assembly](../../../enclosure/freecad/MyFirstQubit_iteration03_candidate_LCD.FCStd)
has two external `App::Link` instances of `CandidateModule`. Keep the component
file with the assembly; FreeCAD must resolve the external document for links.
Original approximate LCD board and active-disk proxies remain hidden and marked
superseded in this new revision only. All previous designs are preserved.

## Physical Dorhea measurements required

Measure both modules individually, including supplier SKU/board revision and
front/back photographs with readable pin labels. Record:

- Total board outline, round section and neck, thickness, edge shape, and hole
  count, diameters and center coordinates from a repeatable datum.
- Actual active circle diameter, glass/bezel outline, center relative to PCB
  and mounting holes, and viewing orientation. Check whether the 0.397 mm source
  center offset exists on the real boards.
- Board-to-glass front/rear heights; FPC, rear components and adhesive stacks;
  safe support surfaces and forbidden display contact areas.
- Header pin order, pitch, style, mounting side, pin/contact heights, solder
  protrusion, mating connector dimensions, insertion/removal sweep, strain relief
  and wire bend space. Do not assume source turned-pin geometry matches ours.
- Tolerances across both boards and lens/retainer stack clearance, including
  off-axis viewing and deformation under validated retention/impact loads.

No precise mounts were fabricated from this reference. Firmware, verified wiring
and all battery requirements remain unchanged; this is still an adult-operated
engineering study, not manufacturing or child-safety validation.
