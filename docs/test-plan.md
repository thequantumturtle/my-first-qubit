# V0.2 breadboard validation

Recorded October 18, 2026. Hardware outcomes reflect the builder's reports during bench testing. This is functional validation, not product qualification.

## Confirmed on hardware

- [x] ESP32-S3 firmware upload succeeds.
- [x] Serial Monitor works with USB CDC On Boot enabled.
- [x] Single GC9A01 draws a circle and phase hand.
- [x] Both GC9A01 displays render independent test colors with separate reset pins.

## Confirmed in the integrated prototype

- [x] GitHub Actions compiles tested firmware e2de5214d59280a63d16a32949b4c171785ba0e4.
- [x] Gate firmware uploads and runs on the ESP32-S3.
- [x] Reset: P(0)=100%, P(1)=0%.
- [x] Reset, X: P(0)=0%, P(1)=100%.
- [x] Reset, H: both fill 50% of area.
- [x] Reset, H, Z: probabilities unchanged and relative phase 180°.
- [x] Reset, H, Z, H: |1⟩ up to global phase.
- [x] Y gate phase-direction checks.
- [x] Gate animation follows the browser reference's complex-amplitude path.
- [x] All seven physical buttons work, including measurement, reset, and colors.
- [x] Both rotary encoders adjust probability and phase.
- [x] Three palettes switch without changing the state.
- [x] Extra outward probability turns preserve amplitudes and global phase.
- [x] The first reverse click registers on both encoders after the detent fix.

## Host checks completed during development

- Gate samples retain normalization and reach X/Y/Z/H endpoints.
- Button bounce, holds, release/repress, and simultaneous-press selection.
- Encoder forward/reverse cycles, bounce, invalid transitions, and both resting contact states.
- Immediate reversals, phase-preserving probability limits, and phase memory at a pole.

These checks used temporary harnesses during the build; they are not yet a repeatable repository test suite. GitHub Actions compiles firmware but cannot test the connected hardware.

## Repeatable bench sequence

1. Reset: left full; right empty.
2. Reset, X: right full. Reset, Y: right full with the hand right.
3. Reset, H: both 50%. Z: right hand down. H: right full.
4. Reset, H, Measure: one result remains full. Repeat from H to check both possible results.
5. Colors: palette changes without changing sizes or hand directions.
6. From reset, 18 increasing probability clicks reach 50/50; another 18 reach |1⟩.
7. At 50/50, turn each knob one click forward and back. Both clicks should register.
8. Turn outward at each probability limit. Nothing should change. Reverse once: sizes should change immediately.

## Still to check

- [ ] Logged 30-minute mixed-use run without resets, display faults, or loose connections.
- [ ] Measurement statistics over a recorded sample; current confirmation is functional only.
- [ ] Fast turns, long leads, and repeatable startup with final control mounting.
- [ ] Improved handling of button presses during an animation, if user testing calls for it.
- [ ] Enclosure layout, permanent wiring, power arrangement, and mechanical retention.

If Serial Monitor shows the right probabilities but displays flicker, check CS connections, power, and SPI wiring. Disconnect USB before adjustments.
