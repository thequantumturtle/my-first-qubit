# V0.1 verified wiring

Two Dorhea 1.28-inch, 240×240 GC9A01 SPI displays on one ESP32-S3.

| LCD signal | Left LCD | Right LCD |
| --- | --- | --- |
| VCC | 3V3 | 3V3 |
| GND | GND | GND |
| SCL / SPI SCK | GPIO 12 | GPIO 12 |
| SDA / SPI MOSI | GPIO 11 | GPIO 11 |
| DC | GPIO 10 | GPIO 10 |
| CS | GPIO 13 | GPIO 14 |
| RST | GPIO 9 | GPIO 8 |

**Verified:** First attempt with a shared reset pin made the left panel fail. Independent RST pins fixed it. Both screens independently filled with test colors.

- Unplug USB before changing wires.
- Use board pin labels, not guessed physical positions.
- Supply 3.3V; don't assume modules tolerate 5V logic.
- Headers must have secure solder connections.
- The serial monitor required USB CDC On Boot: Enabled in this setup.
- SPI frequency in the current sketch: 40 MHz (lower to 20 MHz if wiring is unstable).
- Confirm 3.3V supply headroom before adding more hardware.

Encoder/LED GPIO allocations are not yet tested or locked.
## Physical buttons

H on GPIO 4 has passed a hardware test. The other assignments below are ready for bench testing.

| Button | GPIO | Other connection |
| --- | --- | --- |
| H | 4 | GND |
| X | 5 | GND |
| Y | 6 | GND |
| Z | 7 | GND |
| Measure (M) | 15 | GND |
| Reset state (R) | 16 | GND |
| Colors (C) | 17 | GND |

Unplug USB before wiring. Each normally-open button connects its GPIO to GND when pressed. Firmware enables INPUT_PULLUP; no external resistor or 3.3V button connection is needed. Black jumpers go to the common ground rail; white jumpers go to the assigned GPIOs. Connect that rail to ESP32 GND. Check whether the rail has a break in its middle.

For the four-leg tactile switches, place them across the breadboard center gap. Use diagonally opposite contacts, as with the tested H button. Keep separate signal rows for each button.

Inputs have 30 ms debounce and trigger once per press. Held buttons do not repeat. A button held at startup must be released first. Press one button at a time and let its animation finish. A complete press/release during an animation can be missed. Simultaneous presses select the first button in the table, without queuing the others. Serial commands still work.

Reset (R) resets the qubit state, not the selected palette or the ESP32 itself.

## Rotary encoders (first bench test)

Model: Bourns PEC11R-4225F-S0024, 24 detents and 24 pulses per revolution. See [manufacturer datasheet](https://www.bourns.com/docs/product-datasheets/pec11r.pdf).

| Encoder | A signal | C common (middle of 3-pin row) | B signal |
| --- | --- | --- | --- |
| Probability / balance | GPIO 1 | GND | GPIO 2 |
| Relative phase | GPIO 41 | GND | GPIO 42 |

Each bare encoder has a three-contact row for rotation (A, C, B) and a separate two-contact momentary push switch. Leave the two switch contacts and metal mounting tabs unconnected. Use the center rotation contact for GND, and the outer two for A/B. No VCC connection is required; firmware enables internal pull-ups on A/B. If clockwise decreases rather than increases, unplug USB and swap that encoder's two outer signal wires. Do not move its center GND connection. For a breakout board with labeled pins, use the labels instead of this bare-component layout.

Unplug USB before wiring. Ensure A, C and B each occupy separate breadboard strips; commoned contacts will prevent decoding. The 4-series rear-facing encoder's mounting tabs may not fit the breadboard: use secure leads rather than forcing the body into it.

Each balance click changes theta by 5 degrees, bounded from 0 to 180 degrees. Probability is sin²(theta/2), so clicks are not equal percentage steps. 18 positive clicks from reset reach 50/50, and 36 reach |1>. Each phase click changes relative phase by 15 degrees, wrapping at 360 degrees. At an empty circle, relative phase is undefined; the setting is stored until both amplitudes are nonzero. Knobs preserve the nonzero reference amplitude's phase.

Interrupts count complete quadrature cycles on return to the detent contact state sampled at startup. Leave knobs resting in a click position when powering up. Ordinary bounce and partial reversals do not count; invalid two-bit jumps discard the partial cycle. Probability end stops leave the amplitudes unchanged, including global phase. Moving away from full |1> preserves the surviving amplitude phase. Turns during a gate animation are applied after it finishes. LCD updates are coalesced to the latest accumulated clicks. Start with slow turns; hardware performance and direction still require testing.
