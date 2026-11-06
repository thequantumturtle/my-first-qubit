# Fully 3D-printed enclosure development

For the first physical trial, print only the independent LCD coupon, retainer
and cradle: [print files/settings](prints/lcd-fit-test/README.md),
[illustrated adult assembly/checklist](../docs/lcd-fit-test-assembly.md), and
[dimensioned drawing](freecad/LCD-fit-test-dimensions.svg).
The full enclosure is not released for manufacturing or child use.

| Design stage | Source / review |
| --- | --- |
| Iteration 01: parametric baseline | [native CAD](freecad/MyFirstQubit_enclosure_iteration01.FCStd) |
| Iteration 02: control hierarchy | [layout proposal](iteration02-proposal.md) |
| Iteration 03: calm discovery-board appearance | [design review](freecad/iteration03-review.md) |
| LCD working-model integration and captured lens mounting | [mechanical review](freecad/LCD-mechanical-review.md) |
| Independent 64 x 68 mm LCD fit test | [native CAD](freecad/MyFirstQubit_LCD_fit_test.FCStd) |
| V0.4 battery architecture and packaging study | [power requirements](power-v04.md), [packaging](freecad/v04-battery-review.md) |

The reported Dorhea/model match is qualitative; numerical component dimensions,
mounting strength, optical stack and moving clearances still require physical
verification. See the manufacturing and assembly guides before attaching hardware.

## Current V0.4 power requirement

Normal operation is to use four rechargeable AA NiMH cells in a purchased holder,
rated protection, a regulated supply, and a physical on/off switch. USB becomes
an adult programming/service connection behind a secured closure, not a required
external operating cable. Battery access must be on the underside, adult-only,
with a screw-secured cover and captive fasteners where practical. Reserve voltage
monitoring and future low-battery indication without modifying firmware now.

See [power architecture and verification requirements](power-v04.md) and the
separate [V0.4 battery packaging proposal](freecad/v04-battery-review.md).
Holder selection/dimensions and operating/peak current measurements are pending;
do not add exact mounts or wire an unregulated pack to ESP32 power pins.
The sections below record the initial enclosure direction; Iterations 01-03
remain preserved reference designs.

Design direction: a flat, rounded rectangular busy board with two displays,
probability and phase knobs, and all seven existing buttons: H, X, Y, Z,
Measure, Reset state, and Colors. Reuse the working ESP32-S3 electronics,
verified wiring, and firmware. This supersedes the wood/walnut direction.

This is an adult development engineering prototype. Large controls do not
establish child safety. Child interaction requires a separate safety review.

## Iteration 01 historical baseline

Editable source: `freecad/MyFirstQubit_enclosure_iteration01.FCStd`.
Construction script: `freecad/create_iteration01.py`, executed through FreeCAD
MCP. No existing imported mesh is overwritten and no STL is exported.

FreeCAD is the primary parametric environment. All mechanical files belong
under `enclosure/`. Named spreadsheet parameters drive native Part primitives,
rounded solids, and booleans. Components are independently editable; hidden
construction objects retain their history. Units are millimeters. Origin is
the footprint's lower-left in front view; +Y goes toward the displays and +Z
toward the user. Base underside is Z=0. Parameters ending in `TBD` are unverified
planning envelopes. Other dimensions are proposed choices, not measurements.

| Proposed design choice | Initial value |
| --- | --- |
| Footprint / outer corner radius | 208 x 198 / 14 mm |
| Base height / floor / wall | 30 / 3 / 3 mm |
| Front thickness / joint gap | 3 / 0.3 mm |
| Housing height | 33.3 mm |
| LCD centers / opening diameter (TBD) | (58,151), (150,151) / 34 mm |
| Knob centers / concept diameter | (58,100), (150,100) / 36 mm |
| H, X, Y, Z centers | X=32,80,128,176; Y=57 mm |
| Measure, Reset, Colors centers | X=48,104,160; Y=23 mm |
| Button concept diameter | 26 mm |

Two housing solids form an open-top base tray and removable front panel.
Nominal inner floor footprint is 202 x 192 mm, with 27 mm depth below the rim.
The 0.3 mm seam is provisional, not a validated closure or fit allowance.
No front fasteners, precision mounts, bosses, or inserts are present. The
underside/rear closure and retention remain TBD. The cover and walls surround
the electronics; control openings and the seam mean it is not sealed.
Control concepts and electronics placeholders are separate from housing solids.
They are not finished printable knobs/caps. Shaft/actuator holes are provisional.

## Measurements and unresolved engineering

Physically verify both LCD PCB outlines, thicknesses, active-area positions,
mounting holes, rear headers, and window clearance. Measure the actual ESP32
and breadboard, header/jumper stack, USB connector/plug, and cable bend space.
Measure encoder bodies, tabs, shaft profile/length, mounting interface, and
knob fit. Measure switches, actuator height/travel/force, cap guidance, and load
support. Placeholder envelopes are not verified component drawings.

Planning volumes for ESP32 and breadboard do not prove that the wired prototype
fits or that its switches can sit under the proposed controls without extending
wires. Component retention, display protection, USB opening, strain relief,
permanent wiring, thermal behavior, printer/material assumptions, fastener/tool
access, and cap/knob retention remain unresolved. Serviceability is conceptual
until removable closure and internal supports are designed. Do not treat this
iteration as a final printable assembly.

Validate clearances and print allowances with measurements and fit coupons.
After integration repeat `../docs/test-plan.md`, including both displays, all
seven buttons, both encoders, startup, fast turns, and a 30-minute mixed-use run.
Bench functionality does not qualify the enclosure for child use.
