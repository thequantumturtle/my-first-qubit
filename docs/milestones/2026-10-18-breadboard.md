# V0.2: a working physical qubit simulator

**Date:** October 18, 2026 (America/New_York).

**Hardware-tested firmware:** [e2de5214d59280a63d16a32949b4c171785ba0e4](https://github.com/thequantumturtle/my-first-qubit/tree/e2de5214d59280a63d16a32949b4c171785ba0e4).

**Build evidence:** [successful ESP32 compilation](https://github.com/thequantumturtle/my-first-qubit/actions/runs/39188301749). The builder confirmed the final encoder fixes on hardware. Later documentation changes do not change the firmware.

## Working assembly

- ESP32-S3 N8R8; two Dorhea 1.28-inch, 240×240 GC9A01 LCDs.
- Shared SPI: SCK 12, MOSI 11, DC 10. Left CS 13 / reset 9; right CS 14 / reset 8.
- Seven GND-switched buttons: H 4, X 5, Y 6, Z 7, Measure 15, Reset 16, Colors 17.
- Two Bourns PEC11R-4225F-S0024 encoders: probability A/B 1/2; phase A/B 41/42; both common contacts to GND.
- One shared offscreen framebuffer; 40 MHz SPI. Existing display initialization is preserved.

See [full wiring](../../hardware/wiring.md) before recreating the assembly.

## Lessons retained in the firmware

1. Independent display resets fixed the original two-screen startup problem.
2. Offscreen rendering removed direct black-screen wipes. Full-frame transfers still limit frame rate; gate duration targets 720 ms, with transfer overhead.
3. Each hand shows its amplitude phase. Gate animation follows the browser reference's complex-amplitude evolution, including its chosen global-phase convention.
4. Probability limits must not reconstruct the state. Repeated outward turns previously added saved phase at full |1⟩; limits now leave amplitudes untouched.
5. Count a complete encoder cycle when it returns to the physical detent sampled at startup. This fixed the missed first click after reversing direction.
6. Measurement preserves the surviving amplitude's phase. Relative phase is undefined when either amplitude is zero; the phase control keeps a setting for later.

## Boundaries and next steps

The board classically simulates a single pure qubit. Knobs select discrete angles. Global phase has no single-qubit measurement effect. Measurement/reset transitions are visual interpolation, not quantum gates.

Buttons are polled between animations, so a brief press can be missed during a transition. Simultaneous presses select the first button in the firmware table. Encoder turns are captured by interrupts and applied after an animation.

No completed enclosure, final power design, reliability qualification, or child-use validation is claimed. Next: label controls, record a demo, run the remaining bench checks, and prototype a wooden front panel before permanent assembly.
