# Encoder, knob and button prototype

Engineering prototype, October 23, 2026. No physical fit or strength tests have
been performed. Existing firmware, GPIO assignments, LCD sources, enclosure
iterations and print packages are preserved. This is not a child-safe assembly.

## Native sources and views

- [Full controls study based on PCB160](MyFirstQubit_iteration03_controls_prototype.FCStd)
- [Encoder/knob fixture](MyFirstQubit_encoder_knob_fixture.FCStd)
- [Gate fixture, provisional](MyFirstQubit_gate_button_fixture_PROVISIONAL.FCStd)
- [Measure fixture, provisional](MyFirstQubit_measure_button_fixture_PROVISIONAL.FCStd)
- [Top view](controls-prototype-top.png) and [axonometric](controls-prototype-axonometric.png)
- [Encoder section](encoder-fixture-section.png) and [exploded view](encoder-fixture-exploded.png)
- [Gate section](gate-fixture-section.png) and [exploded view](gate-fixture-exploded.png)
- [Measure section](measure-fixture-section.png) and [exploded view](measure-fixture-exploded.png)
- [Geometry, motion and preservation checks](controls-prototype-validation.json)
- [Construction recipe](create_controls_prototype.py) and [validation/export recipe](validate_export_controls.py)
- [Encoder calibration prints](../prints/encoder-knob-fit-test/README.md)

Each document contains `ControlDimensions`, `ControlConstruction`, separate
`PrintedControlParts`, hardware references and clearance envelopes. Dimensions
ending `TBD` are provisional. Native primitives and booleans carry expressions
for the stack, bores, cap/guide geometry and carriers. Existing PCB160 features
remain as hidden history in the new assembly; `ControlsFrontHousing` adds
encoder posts and enlarged cap passages. Do not print both the historical and
new front housing. Fillet radii are independently editable on native
`Part::Fillet.Edges`; the rounding spreadsheet entries are recipe defaults,
not live links to those edge-radius tuples. Revalidate after any change.

## Component evidence

Exact physical part: **Bourns PEC11R-4225F-S0024** per project inventory.
Manufacturer evidence: [Bourns PEC11R drawing](https://www.bourns.com/docs/product-datasheets/pec11r.pdf),
Rev. 04/26, pages 2–3 inspected visually. Decode: `4` rear-facing PC pins,
`2` 24 detents, `25` shaft length, `F` flatted metal shaft, `S` momentary push,
`0024` 24 pulses. Push contacts remain unused.

| Manufacturer nominal dimension | mm |
| --- | --- |
| Body width / height / depth | 12.5 / 13.4 / 6.5 |
| Shaft diameter | 6.0 ±0.1 |
| Flatted span across shaft | 4.5 +0/−0.05 |
| Mounting-plane to shaft tip, L | 25 |
| Bushing length LB / flat length F | 7 / 12 |
| Bushing thread | **M7 × 0.75** |
| Nut across flats / thickness | 10 ±0.5 / 2 ±0.2 |
| Washer OD / thickness | 12 ±0.3 / 0.5 |
| A–C–B contact pitch | 2.5 |
| Mount-tab center spacing | 13.2 |
| Push travel | 0.5 ±0.3 |

General drawing tolerances also apply. No owned-part caliper readings were
supplied. Bourns specifies a washer and nut; inspect the actual supplied hardware.
The PDF was downloaded for local inspection, not redistributed. Local copy SHA256:
`ac88f657e611bc82fe79b102426fb5abcb7f40740540f0c681727e2d74784491`.
No third-party CAD was imported. This project geometry is a simplified drawing
interpretation; no permission to redistribute the manufacturer PDF is assumed.

PCB footprint XY is referenced from the selected rear-facing drawing: A/C/B
at X−2.5/0/+2.5, Y−7.5, switch contacts X±2.5,Y+7 and tabs X±6.6,Y0.
Pin forms, bend details, rear insertion plane and solder reach remain simplified;
**no precision connection-board drilling pattern is released**.

The existing buttons have only a **generic 6 × 6 mm assortment** description.
No manufacturer, part number, actuator height, travel, force, lead pitch or
terminal drawing is available. CAD uses an explicit hypothesis: 6 × 6 × 3.5 mm
body plus a 1.5 mm actuator, on an unselected 20 × 20 × 1.6 mm PCB. This is
not evidence that the actual switches have a 5 mm overall height. The former
8 × 8 × 6 mm boxes were envelopes, not switch specifications.

## Encoder mounting and load path

A 5 mm faceplate plus nominal 0.5 mm washer and 2 mm nut consumes 7.5 mm,
exceeding the 7 mm bushing before allowing thread margin. Do not clamp this
variant directly through the full 5 mm panel on that assumption.

The prototype uses a **removable internal 3 mm bulkhead**, held on four rear
posts. Its mounting surface is 7 mm behind the faceplate underside. The encoder
body bears against the bulkhead from behind; the supplied washer/nut clamp the
bushing at the front of that internal plate. A shallow rectangular pocket
around the body provides proposed anti-rotation support with 0.5 mm side gaps.
It must not crush case seams or moving parts; inspect actual body tolerances.

In the full assembly: encoder mounting plane Z23.3, bulkhead front Z26.3,
washer/nut top Z28.8 nominal, faceplate underside/top Z30.3/35.3. Nominal unused
bushing beyond nut is 1.5 mm. A 9 mm shaft passage remains in the faceplate;
the nut is hidden inside. Rear access is needed to remove the bulkhead and
reach the nut. Do not apply a metal-panel mounting-torque limit to printed PLA.

Four proposed M2.5 × 8 screws pass through 2.8 mm carrier holes into untested
2 mm panel pilots: 5 mm geometric engagement, 2 mm to blind-pilot end, 2 mm
front roof. These are candidate sizes, not qualified screw/pilot pairings.
The rear carrier/pocket and bushing carry control loads; electrical contacts
and solder joints are not the primary mechanical supports.

The 20 × 24 × 1.6 mm encoder interconnect PCB is an **unselected envelope**,
1 mm behind the simplified case. Rear pin reach 3.7 mm and another 5 mm wiring
reserve are provisional. Choose/design the actual connection board, mounting
and strain relief after measuring pins and tabs; do not bend terminals to fit.
Bourns does not recommend hand soldering in this datasheet: resolve a suitable
assembly process or compatible preassembled board without changing the GPIO map.

## Removable knobs

Both knobs remain **40 mm diameter × 14 mm high**, with 3 mm upper edge rounding.
Balance is sage with one recessed tactile line; Phase is dusty blue with two.
No prominent technical labels are added. Position and color preserve the calm
Iteration 03 hierarchy; the front remains 208 × 198 mm. Future wood knobs may
reuse a separately engineered hub rather than assuming a wood press fit.

The knob underside is 1.3 mm above the faceplate; nominal shaft tip Z48.3 lies
inside the knob ending at Z50.6. The 6.4 mm D-style socket has provisional flat
clearance and 0.5 mm tip clearance. Nominal shaft engagement is 11.7 mm. Maximum
specified encoder push travel leaves 0.5 mm nominal knob/face clearance, before
stack tolerances. The unused push action is not disabled mechanically and no
fixed software end-stop has been invented for Balance.

A recessed **M3 × 16 grub screw candidate** bears on the shaft flat through
a replaceable captive M3 hex nut. Candidate nut envelope is 5.5 AF × 2.4 mm;
trap is 5.7 mm wide × 2.7 mm deep × 6.7 mm high, open from the rear. Verify
actual nut/screw/hex-key dimensions and printed fit. The D socket and screw
avoid reliance on a tight printed friction fit alone; axial pull-off, screw
loosening, trap wear and repeated removal are unqualified. Loose hardware is
an adult-access hazard; no child-safe retention is claimed. Do not glue the
knob permanently or modify the encoder shaft to force retention.

## Captive button mechanism and switch support

Gate surfaces remain 28 mm, Measure 36 mm, Reset/Colors 22 mm. A rounded cap
slides through a passage with 0.3 mm nominal radial clearance. Its rear flange
is 4 mm larger than the visible surface and 1.5 mm thick; it cannot pass through
the smaller front opening. A screw-removable rear guide captures it. A shelf
limits travel to **0.6 mm**, independently of the PCB. These are design values,
not a verified safe operating stroke for the actual switches.

The switch PCB rests on a central nonconducting pedestal beneath the switch
and four corner supports, with two removable edge clips. Press loads follow
cap → actuator/switch body → supported PCB → rear deck → structural columns
and panel, rather than unsupported solder joints. Verify safe copper/component
lands on both PCB faces and insulation needs. Clip screws are provisional M2
with 2.2 mm clearance / 1.5 mm pilot bores; select actual fasteners and lengths
after measuring the board. Model contacts and pilots must not be treated as
qualified threaded joints.

Two candidate M2.5 × 18 stack screws join deck, guide and panel at each button.
Nominal panel engagement is 2.4 mm; the proposed panel pilot is 4 mm deep.
Independent clip removal permits board replacement. All screw access is from
behind; disconnect power, support loose parts and provide actual driver access.

The model leaves 0.2 mm unloaded pusher/actuator gap. Travel-stop minus that gap
would give 0.4 mm actuation in the assumed stack. **Actual travel/pretravel and
overtravel are unknown; do not press a real switch to this stop yet.** Gravity,
return force, cap weight, free play, off-axis jamming and rattling need testing.
Use a measured shim/height adjustment in a subsequent revision; no spring or
preload performance is asserted. Generic switch leads and PCB dimensions are
clearance references only. The present clip arrangement depends on the assumed
PCB outline and needs confirmation before fabrication.

## Clearance and validation findings

The JSON is the numerical record. Checks include single valid closed printed
solids; pairwise printed-part and component-envelope intersections; original
LCD/panel/protection geometry comparison; other electronics envelopes; knob
diameter and button travel parameter changes; depressed cap versus printed
stops; and native-document reopen. Intentional contacts have zero volume.
Electrical pins crossing their hypothetical undrilled PCB are reference
geometry, not a released fabricated-board model.

Full board coordinates remain: displays (58,158)/(150,158), knobs
(58,108)/(150,108); X/Y/Z/H at X32/80/128/176,Y65; Measure (104,28), Reset
(40,28), Colors (168,28). Knob pitch is 92 mm, gap 52 mm. Gate pitch is 48 mm,
gap 20 mm. Knob/display pitch is 50 mm, with 11 mm nominal plan gap to the
38 mm lens. The tightest front control separation is approximately 12.1 mm
between Measure and its diagonal gate neighbors; minimum axis-aligned exterior
edge margin is 10 mm. These are design spacing calculations, not finger-safety
qualification. Rotate a real knob and press caps off-axis before judging comfort.

Button deck is only **0.7 mm above the old breadboard envelope**. Encoder PCB
and wiring envelopes meet the edges of the central wiring reserve; there is
no routing tolerance there. These are packaging warnings despite absence of
volume intersection. Actual wire bundles, new boards, solder and supports may
require relocation of the breadboard or another layout iteration. No battery
proposal consolidation is included, and no extra enclosure depth is claimed.

## Assembly, service and release gates

For encoder calibration: print the small fixture, measure the real encoder,
washer/nut and clamp hardware; trial empty parts first. Insert the body from
behind the bulkhead, fit its washer/nut from the bulkhead front, then secure
the bulkhead to fixture posts. Add the measured nut to the knob, slide the
socket onto the shaft without bottoming, and adjust the recessed screw gently.
Check full rotation, push travel, face clearance, slip and removal by hand.
Disconnect leads without pulling solder joints; remove knob, undo the four
rear screws, withdraw bulkhead, then remove bushing nut for encoder replacement.

For buttons, **measure before printing or assembly**. After revising the real
switch/PCB stack, install cap from behind, guide around its flange, switch on
supported PCB, edge clips and rear carrier. Verify actual actuation and stop
relationship without using the PCB to pull a misaligned stack together. Service
in reverse while supporting the cap. The flange and guide are retention
concepts, not tested child-resistant mechanisms.

Next milestone: obtain dimensioned readings and photos of both encoder variants
in hand and one switch of each used type; select a small supported connection
PCB and actual clamp hardware. Print/test the encoder fixture first. Measure
rotational fit, slip/pull-off, screw/nut durability, axial push clearance and
strain relief. Then revise and release a gate/Measure fixture using measured
actuation travel, return behavior and hard-stop margin. Re-run every working
electrical function only after the unpowered mechanical checks pass.
