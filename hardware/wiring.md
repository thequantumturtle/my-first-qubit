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
- SPI frequency in the current sketch: 10 MHz.
- Confirm 3.3V supply headroom before adding more hardware.

Encoder/button/LED GPIO allocations are *not yet tested or locked*.