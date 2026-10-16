# V0.1 validation plan

## Confirmed on hardware

- [x] ESP32-S3 firmware upload succeeds.
- [x] Serial Monitor works with USB CDC On Boot enabled.
- [x] Single GC9A01 draws a circle and phase hand.
- [x] Both GC9A01 displays render independent test colors with separate reset pins.

## Remaining

- [ ] GitHub Actions builds the gate firmware.
- [ ] Upload gate firmware.
- [ ] Reset: P(0)=100%, P(1)=0%.
- [ ] Reset, X: P(0)=0%, P(1)=100%.
- [ ] Reset, H: both fill 50% of area.
- [ ] Reset, H, Z: probabilities unchanged and relative phase 180°.
- [ ] Reset, H, Z, H: |1⟩ up to global phase.
- [ ] Reset, H, Measure repeated: observe both results; each run collapses to 0 or 1.
- [ ] Test repeated operations and both LCDs for 10 minutes.

If Serial Monitor shows the right probabilities but displays flicker, check CS connections, power, and SPI wiring. Disconnect USB before adjustments.