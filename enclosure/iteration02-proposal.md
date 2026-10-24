# Iteration 02 front-panel proposal

The 208 x 198 mm footprint, 14 mm plan corner radius, 33.3 mm housing height,
and two-piece housing concept are unchanged. Iteration 01's native file and
construction script are preserved. Iteration 02 is an alternative, not a release.

Native source: [iteration 02](freecad/MyFirstQubit_enclosure_iteration02.FCStd).
Views: [top](freecad/iteration02-top.png),
[axonometric](freecad/iteration02-axonometric.png).
The [construction script](freecad/create_iteration02.py) reuses the unchanged
iteration 01 recipe to build a separate document. The Parameters sheet drives
positions, diameters, openings, and placeholder envelopes. The feature tree
retains Housing, ElectronicsPlaceholders, ControlSurfaceConcepts, Construction,
and adds PanelUX with display surrounds and editable visual text concepts.

## Calculations performed before geometry creation

Origin is lower-left in front view; +Y points toward the displays. Units: mm.
All diameters are design choices; 34 mm LCD openings and electronics envelopes
remain unverified TBD values. A 42 mm cosmetic surround emphasizes each display
without asserting a larger active LCD area.

| Item | Center(s) X,Y | Diameter | Minimum panel-edge gap |
| --- | --- | --- | --- |
| Display surrounds | 58,158; 150,158 | 42 (opening 34 TBD) | 19 |
| Probability / Phase knobs | 58,108; 150,108 | 40 | 38 |
| Gates X / Y / Z / H | 32,64; 80,64; 128,64; 176,64 | 28 | 18 / 50 / 50 / 18 |
| Reset / Colors | 40,26; 168,26 | 22 | 15 |
| Measure | 104,26 | 40 | 6 |

Circle distance = sqrt(dx^2 + dy^2). Surface gap = distance minus the two radii.
Edge gaps use the nearest straight footprint edge; none of these circles enters
the rounded-corner regions, so these minima also apply to the rounded outline.

| Pair | Center distance | Surface gap |
| --- | ---: | ---: |
| Display to display | 92 | 50 |
| Display to knob directly below | 50 | 9 |
| Knob to knob | 92 | 52 |
| Adjacent gates | 48 | 20 |
| Probability to Y / Phase to Z | 49.19 | 15.19 |
| Probability to X / Phase to H | 51.11 | 17.11 |
| Measure to Y or Z | 44.94 | 10.94 |
| Reset to X / Colors to H | 38.83 | 13.83 |
| Measure to Reset or Colors | 64 | 33 |

All 55 circle pairs were checked before creating geometry: no overlaps;
the minimum circle gap is 9 mm. Full pair distances are recorded in
`freecad/iteration02-clearances.csv`. The footprint need not grow for this layout.
These gaps do not establish adequate finger space for a particular user.
Measure's 6 mm bottom margin is the main edge-clearance concern. Test grip,
approach angle, inadvertent activation, and finger access on a physical mockup.

Measure has about twice the surface area of a gate and 3.31 times that of a
secondary button. Its centered position, larger diameter, and orange concept
color distinguish it. The gates share a row and color. Reset and Colors are
smaller and muted. Text is a visual labeling proposal, not printable engraving
or a retention feature; labels may need recentering after text/font changes.
The knob labels fit between rows; raised controls can occlude them obliquely.

## Validation and unresolved work

The housing and component placeholder solids are valid; no housing/electronics
placeholder volume intersections were found. This checks only modeled planning
envelopes, not wiring, headers, fingers, cable bends, or moving mechanisms.
Iteration 01's native file SHA256 was unchanged after generation:
`b4eb6c7f5582d7056a2977a869e44e7ea3d882f4b6f8ac3777b8f813fb5a859f`.

All actual dimensions still require physical verification as listed in the
enclosure README: LCD boards/windows, ESP32, breadboard stack, encoder shafts,
switch travel, headers, USB plug, wiring and tool clearances. The 42 mm display
surrounds are independent concept parts, not validated window protection.
All control retention, cap guidance, load paths, cover closure, service access,
strain relief, and child-safety requirements remain unresolved. This proposal
is not ready for child use or final printing. No firmware changes or STL exports
are part of this iteration.
