# My First Qubit: development guidance

## Project architecture and evidence

This is an ESP32-S3 physical learning board that classically simulates one pure
qubit. It is an engineering prototype, not a quantum processor or a child-safe
toy. Child interaction requires a separate safety review.

- `README.md`: setup, user controls, and project overview.
- `firmware/MyFirstQubit/MyFirstQubit.ino`: Arduino sketch containing complex
  amplitudes, X/Y/Z/H gates, measurement/reset, palettes, rendering, button
  polling, and interrupt-driven encoder decoding.
- `hardware/wiring.md`: connections and bench wiring precautions.
- `hardware/components.md`: inventory and previously deferred purchases.
- `docs/test-plan.md`: confirmed behavior, repeatable bench sequence, and open
  validation tasks.
- `docs/milestones/2026-10-18-breadboard.md`: working breadboard milestone and
  hardware-tested firmware reference, `e2de5214d59280a63d16a32949b4c171785ba0e4`.
- `enclosure/`: all mechanical design sources, exports, measurements, assembly
  instructions, and enclosure-specific documentation.
- `enclosure/prints/lcd-fit-test/`: only the three fit-test STLs, manufacturing
  instructions and export validation; never include electronics or a whole
  enclosure in these print meshes.
- `hardware/models/`: purchased component reference models, originals and their
  license/attribution; this component-library location is an explicit exception
  to keeping enclosure design files under `enclosure/`.
- `.github/workflows/arduino.yml`: Arduino CLI compile check for
  `esp32:esp32:esp32s3`, with the Espressif core, Adafruit GC9A01A, and Adafruit
  GFX Library. A successful compile does not validate connected hardware.

The recorded October 18, 2026 milestone reports integrated hardware success.
Host checks used temporary harnesses; there is no repeatable repository host
test suite. Do not present recorded results as newly performed verification.

## Current hardware configuration

Reuse the working ESP32-S3 N8R8 DevKitC-style board, breadboard electronics,
two Dorhea 1.28-inch 240x240 GC9A01 seven-pin SPI modules, seven normally-open
tactile buttons, and two Bourns PEC11R-4225F-S0024 encoders wherever possible.
Six encoders were ordered; only two are in use. Encoder push switches are unused.

| Function | GPIO / connection |
| --- | --- |
| Shared LCD SCK / MOSI / DC | 12 / 11 / 10 |
| Left LCD CS / RST | 13 / 9 |
| Right LCD CS / RST | 14 / 8 |
| Both LCD supplies | 3V3 and GND |
| H / X / Y / Z buttons | 4 / 5 / 6 / 7 |
| Measure / Reset state / Colors buttons | 15 / 16 / 17 |
| Probability encoder A / B | 1 / 2 |
| Relative-phase encoder A / B | 41 / 42 |

Buttons connect their GPIO to GND using internal pull-ups. Each encoder's center
rotation contact is common to GND; A/B use internal pull-ups with no VCC
connection. Leave encoder push contacts unused. Preserve independent LCD reset
pins: sharing reset previously caused a display startup failure. Display SPI
runs at 40 MHz using one shared offscreen framebuffer.

Disconnect USB before wiring changes. Use actual board labels, secure solder
connections, and verify breadboard rail continuity. Do not assume 5V logic
tolerance or spare supply capacity. Preserve the working flash/PSRAM settings;
the documented setup uses ESP32S3 Dev Module, USB CDC On Boot enabled, and
115200-baud serial. Keep USB programming and serial diagnostics accessible.

## Behavior that enclosure work must preserve

### Planned V0.4 battery power (not yet wired or electrically validated)

Normal operation must not require an external USB cable. Use four rechargeable
AA NiMH cells in a purchased four-cell holder, rated protection and a regulated
supply, and a physical on/off switch. Provide adult-only underside access with
a screw-secured cover and captive fasteners where practical. USB programming
and service must remain adult-accessible behind a secured closure, with no
exposed service opening during any future approved child use. Provide space
for voltage sensing and eventual low-battery indication; no GPIO or firmware
change is authorized by this requirement.

Before exact mounts or electrical ratings are chosen, identify and physically
verify the loaded holder, and measure operating and peak current with both LCDs
active. Provisional CAD envelopes do not establish selected component dimensions.
Never connect raw pack voltage to unverified ESP32 power pins. Verify the actual
board revision, regulation and USB power isolation; disconnect all power sources
before wiring changes. See `enclosure/power-v04.md` for architecture, measurement
gates, charging policy, and unresolved safety requirements. The recorded USB bench
configuration remains historical working evidence, not the V0.4 power design.

- Both displays independently show probability by filled area and each complex
  amplitude's phase by a hand. Keep both views and their labels unobstructed.
- Retain all seven physical actions: H, X, Y, Z, Measure, Reset, and Colors.
  Reset returns to exactly |0> and preserves the palette; it is not MCU reset.
- Retain both encoders: probability changes theta by 5 degrees per click with
  software limits from 0 to 180 degrees; phase changes by 15 degrees per click
  and wraps. The encoders physically rotate; software probability limits do not
  imply mechanical stops. Preserve usable rotation and immediate reversal.
- Phase memory at a probability pole, amplitude phase preservation, measurement
  collapse, and three palettes are existing behavior, not mechanical redesign
  opportunities. Encoder push switches do not replace any existing control.
- Buttons debounce at 30 ms and do not repeat when held. Animations block button
  polling, so brief presses may be missed; simultaneous presses select the first
  in firmware order. Encoder turns accumulate during animations and apply later.
  Start encoders at a detent. Do not promise improved input handling without a
  separately scoped firmware change.

## Enclosure direction and CAD conventions

Develop a fully 3D-printed, flat busy-board-style enclosure with large, intuitive,
clearly labeled physical controls and an enclosed, serviceable electronics
compartment. Reuse current controls with suitable printed interfaces where
feasible; establish fit and actuation before proposing replacement electronics.
Service access must allow repair without destroying the printed housing, with
access to wiring, connectors, mounting hardware, and the ESP32 USB interface.
Plan secure component retention, display protection, wire routing, connector
clearance, cable strain relief, and protection against control loads reaching
PCBs or solder joints. Final retention, power arrangement, and layout remain
design work, not established hardware facts.

- Use FreeCAD as the primary parametric mechanical CAD environment. Native
  `.FCStd` documents are the editable source of truth; printable mesh exports
  are derived artifacts. Keep both, and any generation scripts, under `enclosure/`.
- Use millimeters and named parameters for component dimensions, spacing,
  clearances, wall thicknesses, and fasteners. Prefer constrained sketches and
  understandable feature names over unexplained fixed geometry.
- For future models, use the front panel in XY with +Z toward the user; define
  and document the origin and left/right orientation before laying out parts.
- Separate measured component dimensions, sourced nominal dimensions, proposed
  design choices, and printer-fit allowances. Record sources, measurement dates,
  and verification status in `enclosure/`. Label unknowns `TBD: physical
  verification required`; do not silently turn guesses into production geometry.
- Establish printer/material/process assumptions and validate fits with small
  coupons before a full enclosure print. Document assembly and disassembly.

### Physical verification required before detailed CAD

Nominal screen size, pixel count, component model names, the inventory's 6x6 mm
button description, and the deferred knob's nominal 6 mm D-flat fit are not
verified mounting dimensions. Measure the actual parts and assembled stack:

- Both LCD PCB outlines, thicknesses, mounting-hole locations/diameters, active
  display position, bezel/window clearance, and rear component/header envelope.
- ESP32 board and breadboard outlines, heights, mounting options, header and
  jumper envelopes, USB connector location, plug envelope, and cable bend space.
- Encoder bodies, tabs, terminals, mounting interface, shaft length/diameter and
  flat geometry, knob engagement, rotation clearance, and axial movement.
- Actual switch bodies, pitch, actuator height/travel, force, and printed cap
  guidance/retention needed to avoid binding or excessive switch loads.
- Actual wire bundles, connector access, fasteners/inserts, tool access,
  compartment depth, and total stack height. Determine print-fit allowances
  experimentally rather than claiming universal tolerances.

Do not invent precise dimensions or infer module PCB dimensions from a
1.28-inch display diagonal. Manufacturer drawings may inform parameters but
must be checked against the parts in hand.

## Development constraints and validation

The initial guidance-only review is complete. Current user-authorized mechanical
work may create CAD and the LCD fit-test print exports. Keep enclosure design files
under `enclosure/` and preserve the verified GPIO map and working electronics
unless a change is explicitly scoped and justified.

Before exporting fit-test meshes, reopen the native fit-test file, select only
the panel coupon, lens retainer and rear cradle, and validate single closed
solids plus round-tripped mesh topology and millimeter bounds. Use
`enclosure/freecad/export_lcd_fit_test.py`; do not save over historical CAD sources.
Record export validation separately from actual printer accuracy and physical
fit results. See `docs/lcd-fit-test-assembly.md` before assembly or powered tests.

Older documentation describes a wood enclosure, walnut knobs, and six larger
buttons; these are historical directions, superseded for new mechanical work
by the fully printed enclosure and preservation of all seven actions. The
wiring sentence saying encoder allocations are untested is stale relative to
its later tested encoder section, the sketch, and the milestone. Inventory
and wiring V0.1 headings coexist with the V0.2 tested breadboard milestone.
Do not silently treat these old notes as current mechanical requirements.

After physical integration, repeat `docs/test-plan.md` with both displays and
all controls. Open work includes a logged 30-minute mixed-use run, recorded
measurement statistics, fast encoder turns, longer leads, reliable startup
with final mounting, permanent wiring, power, and mechanical retention. Add
fit, assembly/service access, control binding, cable routing, and retention
checks as the enclosure develops. Firmware compilation alone is insufficient.

Maintain adult-supervised engineering-prototype status. An enclosed compartment
or large controls do not establish child safety. Separate review before child
interaction must address retention, small parts/choking, pinch points, guarded
electronics, cable strain relief, materials/finishes, and applicable safety
requirements; do not claim toy qualification from functional bench testing.
