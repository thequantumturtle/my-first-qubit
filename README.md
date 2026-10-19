# My First Qubit

Montessori-inspired single-qubit physical learning board by **The Quantum Turtle**.

**Status: V0.2 tested breadboard milestone, October 18, 2026.** Two round displays, seven buttons, and two rotary encoders work together on an ESP32-S3 N8R8. This classically simulates one pure qubit; it is not a quantum processor or a finished children's toy.

The hardware-tested firmware is [commit e2de521](https://github.com/thequantumturtle/my-first-qubit/tree/e2de5214d59280a63d16a32949b4c171785ba0e4). Its [ESP32 compilation passed](https://github.com/thequantumturtle/my-first-qubit/actions/runs/39188301749). See the [milestone record](docs/milestones/2026-10-18-breadboard.md) for tested behavior and remaining work.

## Quick start

1. See [wiring](hardware/wiring.md) and disconnect USB before changing wires.
2. Install Arduino IDE 2, Espressif ESP32 board support, Adafruit GC9A01A and Adafruit GFX Library.
3. Open `firmware/MyFirstQubit/MyFirstQubit.ino`.
4. Choose **ESP32S3 Dev Module**, **USB CDC On Boot: Enabled**, and the connected serial port.
5. Upload and open Serial Monitor at **115200 baud**.
6. Leave both encoders resting in a click position at startup. Send `R` reset, `X`, `Y`, `Z`, `H` gates, `M` measure, or `C` colors. Keep your existing working flash/PSRAM settings.

Each filled disk has **area proportional to probability** (radius ∝ √probability). Each hand shows its own complex amplitude's phase, clockwise from up. Only the difference between phases can affect single-qubit interference; global phase does not affect measurement results. An empty circle has no phase hand.

## Physical controls

| Control | GPIO | Action |
| --- | --- | --- |
| H | 4 | Hadamard gate |
| X | 5 | X gate |
| Y | 6 | Y gate |
| Z | 7 | Z gate |
| Measure | 15 | Sample 0 or 1 and collapse the state |
| Reset | 16 | Return to exactly \|0⟩; keep the palette |
| Colors | 17 | Cycle Woodland, Garden, and Night |
| Probability encoder A/B | 1 / 2 | Change balance angle θ by 5° per click |
| Phase encoder A/B | 41 / 42 | Change relative phase φ by 15° per click |

Each button connects its GPIO to GND. Each encoder's center rotation contact connects to GND; the outer contacts connect to A/B. Internal pull-ups are enabled. Encoder push switches are unused.

The probability control uses P(1) = sin²(θ/2), so equal clicks do not make equal percentage changes. From reset, 18 increasing clicks reach 50/50 and 36 reach |1⟩. Probability has end stops; phase wraps. At either probability pole, the phase knob stores a setting until both amplitudes are nonzero. The pure-state model is general; the knobs select discrete angles. Mixed states are not modeled.

Buttons do not repeat when held. Press one at a time and let the animation finish. A brief press during an animation may be missed; encoder turns are counted and applied afterward. Colors change only the palette.

Try `R` → `H` → `Z` → `H`: the state should become |1⟩ up to global phase.

- [Firmware](firmware/MyFirstQubit/MyFirstQubit.ino)
- [Wiring](hardware/wiring.md)
- [Components](hardware/components.md)
- [Test plan](docs/test-plan.md)
- [Enclosure notes](enclosure/README.md)

[Interactive web prototype](https://thequantumturtle.github.io/learn/my-first-qubit/)

[Build journal](https://thequantumturtle.github.io/work/building-my-first-qubit/)

**Safety:** This breadboard assembly is for adult development, not use as a toddler toy.
