# My First Qubit

Montessori-inspired single-qubit physical learning board by **The Quantum Turtle**.

**Status:** V0.1 breadboard prototype. Two Dorhea 1.28-inch GC9A01 SPI LCDs have been demonstrated with an ESP32-S3. Separate reset pins were required. Serial-driven quantum-gate firmware still requires hardware validation.

## Quick start

1. See [wiring](hardware/wiring.md) and disconnect USB before changing wires.
2. Install Arduino IDE 2, Espressif ESP32 board support, Adafruit GC9A01A and Adafruit GFX Library.
3. Open `firmware/MyFirstQubit/MyFirstQubit.ino`.
4. Choose **ESP32S3 Dev Module**, **USB CDC On Boot: Enabled**, and the connected serial port.
5. Upload and open Serial Monitor at **115200 baud**.
6. Send: `R` reset, `X`, `Y`, `Z`, `H` gates, or `M` measure.

Each filled cyan disk has **area proportional to probability** (radius ∝ √probability). The yellow clock hand shows relative phase when both amplitudes exist.

Try `R` → `H` → `Z` → `H`: the state should become |1⟩ up to global phase.

- [Firmware](firmware/MyFirstQubit/MyFirstQubit.ino)
- [Wiring](hardware/wiring.md)
- [Components](hardware/components.md)
- [Test plan](docs/test-plan.md)
- [Enclosure notes](enclosure/README.md)

[Interactive web prototype](https://thequantumturtle.github.io/learn/my-first-qubit/)

**Safety:** This breadboard assembly is for adult development, not use as a toddler toy.