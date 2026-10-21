# V0.4 battery power requirements and verification gates

Status: architecture and provisional packaging only. No powered battery assembly,
selected holder, measured load, approved schematic, or child-use qualification.
The existing ESP32-S3/two-LCD/two-encoder/seven-button wiring and firmware remain
unchanged. Historical bench operation uses USB; normal V0.4 operation must not
require an external power cable.

## Architecture

Four rechargeable AA NiMH cells in series in a purchased four-cell holder feed
source-proximate short-circuit protection, reverse-polarity protection, a physical
on/off disconnect, and an appropriately rated regulated supply. The exact order
and implementation of protection/switching must be reviewed in the schematic.
The regulated output feeds only a verified board input and the verified LCD
power path. Return currents and grounding must be designed explicitly.

The nominal pack is 4.8 V based on four nominal 1.2 V NiMH cells; this is not a
regulated rail or a maximum/minimum design voltage. Determine the selected cells'
fresh-charge maximum, loaded discharge range, imbalance behavior and end-of-life
limits from their data and measurement. If a verified 5 V input is chosen, assess
a buck-boost supply across the required pack range; a simple buck or boost may
not cover it. A dedicated 3.3 V path requires separate board/backfeed review.
No regulator topology, part, output connection, current rating, cutoff voltage,
wire gauge, fuse value, or switch rating is selected here.

Never connect raw battery voltage directly to unverified ESP32 5V/VIN/3V3 pins
or any signal pin. The installed board is only described as DevKitC-style;
manufacturer documentation for a genuine board does not establish clone wiring.
Espressif documents mutually exclusive power-input options for the genuine
[DevKitC-1 v1.1](https://documentation.espressif.com/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html).
Verify the actual board schematic/revision and both USB port power paths before
any battery connection. A USB/battery interlock or verified power-path isolation
must prevent backfeeding the host, regulator, pack, or another USB connector.
The on/off state alone does not prove isolation, especially through sensing or
regulator paths. Until isolation is validated, battery power must be physically
disconnected for adult USB service; never experiment with simultaneous supplies.

Reserve protected voltage sensing (divider/filter or monitor IC), but do not
select a GPIO, resistor values, or firmware now. Any future input must stay within
the verified ADC limits at maximum pack voltage, component tolerances and faults,
including when the MCU is off; prevent phantom powering. Assess divider drain,
reference accuracy, ADC calibration, and voltage sag under load. Low-battery
indication is future UI functionality, not battery protection. Hardware cutoff
and undervoltage hysteresis must not depend solely on future application code.

For this proposal, remove cells for charging in a suitable external NiMH charger
under adult control. There is no in-device charger or USB charging function.
No trickle-charging, Li-ion charging board, or chemistry substitution is implied.
[Panasonic's NiMH handbook](https://energy.panasonic.com/dam/master/pdf/eu/material/Panasonic_Ni-MH_Batteries_Handbook.pdf)
identifies damage from deep discharge/reverse charging. A pack-average voltage
does not prove the weakest cell is protected; assess cell imbalance and reversal
with the selected cells. Use matched cells per their manufacturer's instructions.

## Required measurements before exact mounting or supply selection

1. Select a holder part number and cell model. Obtain their drawings, ratings,
   materials, contact style and mass; physically verify the purchased loaded
   holder's full length/width/height, springs, lead exit, insertion/removal sweep,
   polarity markings, mounting provisions, connector and wire bend envelope.
   Capture uncertainty and samples; do not treat the CAD allowance as a drawing.
2. With the unchanged working firmware and both LCDs active, measure steady
   operating current and peak/startup current at the current verified supply
   interface. Use the existing safe supply arrangement; no raw-cell hookup is
   required for this test. Record supply voltage, measurement point, instrument,
   sampling bandwidth, shunt/burden effects and board/reset behavior.
3. Exercise cold boot, both display initialization, repeated gates, measurement,
   palette changes, both encoders, and a logged mixed-use run. Test actual current
   firmware behavior, including any radio state; do not invent future loads.
   Capture brief transients with suitable equipment; a handheld average reading
   alone is not a peak-current measurement. Also measure off-state drain after
   the proposed power path exists, including regulator and monitor leakage.
4. Once a candidate regulated path is reviewed, use a current-limited bench
   source across its approved input range. Log battery-side and output currents,
   output droop/ripple, startup/inrush and efficiency. Convert power, not merely
   equal current between different voltage rails. Validate recovery and cutoff
   near low battery, fresh-charge input and thermal steady state in an enclosure.
5. Choose protection, switch, wiring, connectors and regulator with documented
   transient/continuous/temperature margin. Then finalize mounts, ventilation or
   thermal spacing, retention and runtime estimates. Do not claim runtime from
   nominal capacity and an unmeasured load.

| Required record | Current status |
| --- | --- |
| Holder/cell part numbers and drawings | Not supplied/selected |
| Loaded holder measured XYZ, mass, mounting and removal envelope | Not measured |
| Steady operating current at known input voltage | Not measured |
| Startup/peak current, duration, instrument bandwidth | Not measured |
| Converter efficiency, output droop, thermal and off-state behavior | Not measured |
| Board input and USB isolation verification | Pending |

## Mechanical access and unresolved electrical safety

Provide underside adult-only battery access through a screw-secured cover, with
captive fasteners where practical. Cell retention must not depend on the outer
cover alone. No exposed front screws, loose removable plugs, or child-accessible
service openings. Keep USB behind a secured service closure and accessible to
adult tools/plugs without removing cells through exposed live contacts. The CAD
currently reserves a switch inside the lower service bay; ergonomic switch access
and its independent guard/closure remain unresolved. Do not leave the battery
cover open during operation to reach it.

The new cover is only conceptual and has no screw holes or captive mechanism;
it is not yet secured. Screw positions, inserts, captive details and service-door
geometry must be designed after holder, hardware and access requirements are
verified. Printed press fits do not establish adult-only access. Battery contacts,
bare wiring, hot components and USB must remain inaccessible in any future
approved child-use configuration.

Unresolved review items include source-proximate fault protection and its energy
let-through, reversed cell/pack insertion, holder contact heating and reliability,
wire/connector/switch DC and inrush ratings, short circuits, regulator failure and
overvoltage, weak-cell reversal, deep discharge, unintended USB charging/backfeed,
off-state leakage, thermal behavior, battery leakage/venting without a sealed
pressure trap, insulation, strain relief, enclosure material response and access
after drops or repeated servicing. Do not perform unreviewed fault tests with
unprotected cells. A battery holder and regulator are not themselves a complete
protection system. No electrical or child-safety claim follows from passing CAD.
