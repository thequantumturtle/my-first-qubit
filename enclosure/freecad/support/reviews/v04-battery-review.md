# V0.4 provisional battery packaging

Native proposal: [FreeCAD](MyFirstQubit_enclosure_v04_battery_proposal.FCStd).
Views: [exterior](v04-battery-exterior.png),
[underside with cover hidden](v04-battery-underside-open.png).
[Recipe](create_v04_battery_proposal.py) and
[validation results](v04-battery-validation.json) retain the design evidence.
See [power requirements](../power-v04.md) for electrical gates and pending data.

This clones iteration 03; iterations 01-03 are checksum-preserved. The front,
all seven buttons, both encoders, displays and existing electronics are retained.
BatteryParameters drives the new native Part geometry and independently editable
envelopes. Every component dimension is an unverified planning allowance, not a
selected holder/regulator drawing. No exact battery mounts or fasteners are made.

## Packaging and thickness

An isolated full-footprint lower bay sits below the original electronics floor,
which forms the compartment's ceiling/partition. The underside cover is a separate
3 mm solid. The added lower walls and cover are not yet fastened to each other
or to the original tray. The cover MUST become screw-secured, with captive
fasteners where practical; no present geometry demonstrates secure access.

| Planning object | XYZ envelope mm | Center XY mm | Z range mm |
| --- | --- | --- | --- |
| Four cells plus purchased holder | 70 x 65 x 20 | 104,99 | -22..-2 |
| Regulator module allowance | 35 x 25 x 12 | 164,99 | -20..-8 |
| Protection allowance | 20 x 20 x 10 | 44,99 | -20..-10 |
| Physical on/off switch allowance | 25 x 15 x 12 | 104,150 | -20..-8 |
| Voltage-monitor allowance | 20 x 15 x 8 | 164,135 | -20..-12 |

This conservative, separated packaging study adds **26 mm**: housing thickness
increases from **35.3 to 61.3 mm**. Overall height including knobs increases from
49.3 to 75.3 mm. The front stays at Z=35.3 and the new underside is Z=-26; the
208 x 198 mm footprint is unchanged. This is not a calculated minimum thickness.
The layer follows 3 mm cover + 1 mm bottom gap + 20 mm loaded-holder allowance
+ 2 mm ceiling gap. After measurements, compare alternate purchased holder
layouts and reuse of existing voids before accepting the thicker form factor.
Do not scale unmeasured holder geometry to make the design appear flatter.

Geometry checks found no invalid final solids and no unintended volume
intersections among new power envelopes, original electronics, wiring reserve,
optical parts, controls and housing. Holder-to-ceiling clearance is 2 mm, to cover
1 mm, to regulator 7.5 mm, and to protection 15 mm. These are static envelope
gaps only, not electrical spacing, thermal clearance, assembly/tool access or
cell-removal validation. There is no modeled harness, switch actuator, USB service
door or new fastener pattern. The lower bay contains power circuitry as well as
the holder; its cover is adult service access, not a validated battery-only door.

## Weight distribution assessment

The loaded-holder planning center is (104,99,-12), directly beneath the footprint
center. Assuming the real loaded holder's mass center matches that point, it
adds no lateral tipping moment about the center. That assumption must be measured.
The regulator/monitor lie to the right and protection lies to the left; there is
no evidence their masses balance. The switch is offset toward the upper edge.
Existing LCDs, printed controls, housing, wiring and breadboard also contribute.

No measured masses exist, so actual total mass, center of gravity and tipping
margin are not reported. The mass worksheet records CAD envelope centroids with
blank mass fields; these are not verified component mass centroids. Use
COM = sum(m_i * r_i) / sum(m_i) once masses and their positions are measured.
For sensitivity only, each 10 g at X=164 contributes +600 g*mm of lateral moment
about X=104, moving total COM by 600/M mm where M is assembled mass in grams.
Each 10 g at X=44 contributes -600 g*mm. These are equations, not measured masses.

Low battery placement may help concentrate mass near the support, but the added
layer also raises existing electronics relative to the support plane. Do not
claim stability improves without weighing and checking the complete assembly.
Support footprint, feet, friction, cover deflection and realistic control loads
remain unverified. Recheck balance with cells installed/removed and after service.

## Next gates

Select and physically verify holder/cells; measure operating and peak current
with both LCDs active; choose the protected regulated supply and confirm the exact
board input/USB isolation. Then optimize thickness, close the mass budget, design
positive holder retention, screw-secured/captive cover details, isolated adult USB
service access, switch access and wiring. No raw pack connection to unverified
ESP32 pins is authorized. No firmware change, battery measurement, runtime claim,
STL export or child-handling qualification is part of this proposal.
