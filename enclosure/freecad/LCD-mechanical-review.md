# LCD mechanical integration: Iteration 03 serviceable mounting revision

Adult-operated engineering prototype. The user reports that the physical Dorhea
modules have been checked and match the imported META-MCU model. The imported
model is now the **working mechanical reference** for mounting design. This is
not evidence of a completed dimensional inspection or safety assessment.

## Deliverables

- [New enclosure assembly](MyFirstQubit_iteration03_LCD_mechanical_integration.FCStd)
- [Independent compact fit-test assembly](MyFirstQubit_LCD_fit_test.FCStd)
- [Dimensioned fit-test drawing, SVG](LCD-fit-test-dimensions.svg)
- [Mounting-system exploded view](LCD-mount-exploded.png)
- [Mounting-system section view](LCD-mount-section.png)
- [Installed mounting system](LCD-mechanical-inside.png)
- [Assembled fit test](LCD-fit-test-assembled.png)
- [Three-part print layout](LCD-fit-test-print-layout.png)
- [Geometry and clearance data](LCD-mechanical-validation.json)
- [Lens-gap study](LCD-lens-gap-study.json)
- [Construction recipe](create_lcd_mechanical_integration.py) and
  [dimension-drawing generator](document_lcd_fit_test.py)

All earlier native assemblies, the battery proposal, imported component document,
original STEP/drawing, license and other component reference files are preserved.
Protected file hashes are recorded in the validation report. The new assembly
uses the earlier candidate-placement revision, which is based on Iteration 03.
It does not yet merge the V0.4 lower battery compartment; battery requirements
remain active for subsequent consolidation. Firmware and wiring are untouched.

## Confirmation register: what is and is not measured

| Item | Status in this revision |
| --- | --- |
| Actual Dorhea modules match the imported model | Confirmed qualitatively by the user's report |
| Permission to use the model for mechanical integration | Established by this task |
| Presence of existing LCD mounting holes | Established by the reported match and task; use modeled axes as working references |
| Individual hole diameters/coordinates, PCB outline/thickness, glass/header stack | Numerical values are imported-model values; no individual caliper readings or tolerances supplied |
| Physical pin order, solder envelope, cable/mating connector, backside contact areas | Not individually confirmed; verify physically before fasteners are tightened |
| Lens stock and optical active diameter/position, impact strength, retention | Provisional and untested |

No exact numerical component dimension is newly marked physically measured.
The historical reference README and native component still contain their earlier
candidate labels; those files were intentionally preserved. New assembly link
labels and this dated register supersede their match status for this study.

Working model values include 23 mm hole pitch, diameter 2.10 mm holes, a
0.41148 mm PCB, a 35.2 mm simplified LCD body, and the existing connector model.
The drawing/model discrepancies documented in the reference remain relevant.
Extra decimal places locate geometry; they do not imply real component precision.

## Mounting and load paths

Each LCD uses two integral front-panel standoffs on the existing PCB hole axes,
not a symmetric pattern guessed from the LCD center. The model's display/PCB
center offset is retained. Each standoff is diameter 4.6 mm and extends 1.5 mm
behind the original panel underside at the current stack. A proposed 1.6 mm blind
pilot extends 5 mm into the post/panel, leaving 1.5 mm of front material above it.
There are no screw openings on the front face.

A separate printable rear cradle has 52 mm outer width, 3 mm rails, a 2 mm base
thickness, two neck clamps at the mounting holes, and two backside support pads
at local (+/-12,+12) mm. Four raised contact lands bridge a provisional 1.2 mm
space behind the PCB; the rest of the cradle stays below that space. These lands
must be checked against actual rear components and traces. No support contacts
the modeled active LCD/front glass. Do not clamp the glass or use the cradle to
straighten a warped board. Actual support eligibility and clamp torque remain TBD.

Two proposed M2 x 8 thread-forming screw envelopes per PCB pass through 2.4 mm
cradle clearance bores and the existing modeled PCB holes into the blind pilots.
CAD engagement is about 4.39 mm, with about 0.61 mm to the end of the pilot.
These are **fastener design assumptions**, not selected hardware specifications.
The 2.10 mm PCB-hole / 2.00 mm nominal screw assumption has little radial margin;
do not force a screw into a real board. Test the actual fastener and FDM pilots.
The 4.4 mm neck pad and 3.8 mm head envelope leave only 0.3 mm radial bearing
margin. Strength, washers, pilot sizing, repeated service and thread durability
must be tested. Do not substitute longer screws: they could pierce the face.

## Captured lens system

Each separate transparent lens remains provisional clear polycarbonate,
diameter 38 x 1.5 mm. The 34 mm front optical aperture leaves 2 mm radial lip
overlap; the lens front is recessed 1 mm. The 38.6 mm pocket gives a proposed
0.3 mm radial lens allowance. No adhesive-only retention is used.

The new rear retainer is independently removable. Its stepped geometry has:

- A 48 mm outer flange with 40.6 mm bore and a lower neck relief clearing PCB
  and header; the flange is 1.5 mm thick.
- A 0.7 mm shoulder seated in a new 49 mm rear panel counterbore.
- A full annular lens-bearing nose, OD 38.4 / ID 36.4 mm, extending to the lens
  rear perimeter. Lens bearing overlap is only 0.8 mm radially and the nose wall
  is 1 mm; this needs retention/impact and FDM-strength testing.
- Two side tabs, diameter 7 mm at local (+/-25,0), with 2.4 mm clear holes.
  Proposed rear M2 x 4 screw envelopes engage panel pilots by 2.5 mm. No front
  screw holes, exterior lens edges, or bonding to the LCD are introduced.

The nominal axial lens stack has zero free play. It is not an approved lens
clamping preload: measure lens stock, assess thermal expansion and deformation,
and determine a controlled compliant interface if needed. A thin unvalidated
printed lip is not evidence that a lens cannot be pushed through or pried out.

## Display-to-lens reduction and clearances

The unchanged lens rear plane is at assembly Z=32.8 mm. The working LCD front
is moved from Z=27.3 to **30.8 mm**, reducing the nominal gap from **5.5 to 2 mm**.
The PCB front is Z=28.8000 and its back Z=28.3885 using the source stack. Lens,
panel, PCB and cradle heights are derived live from named spreadsheet parameters.

The old 34 mm-bore retainer prevented moving the LCD forward. The larger 36.4 mm
bore now clears the 35.2 mm LCD body by 0.6 mm radially. A new 19 x 5 x 2.2 mm
rear header pocket clears the connector's forward protrusion without a through
opening. The resulting minimum connector-to-panel surface gap is about 0.65 mm.

| Nominal lens gap | Header / panel gap | PCB pilot roof | CAD result |
| --- | ---: | ---: | --- |
| 2.0 mm, retained | 0.65 mm | 1.50 mm | No header collision |
| 1.5 mm, tested temporarily | 0.15 mm | 1.00 mm | Too little unvalidated margin to adopt |
| 1.0 mm, tested temporarily | Intersects | 0.50 mm | Approximately 1.14 mm^3 header/panel overlap |

All temporary gap changes were reverted to 2 mm. These tests establish geometry,
not safe clearance under impact, thermal expansion, PCB flex or tolerance stack.
Do not reduce the gap solely because a static CAD overlap check passes. The LCD
body is not a detailed active-area model: verify actual viewing area, centering
and oblique visibility through the 34 mm aperture before committing the window.

At the final stack, the digital glass/body-to-lens distance is 2 mm and its
nearest distance to the lens retainer is 0.6 mm. Header-to-cradle minimum gap is
about 0.41 mm, which is a tight provisional clearance needing a physical check.
Both mount systems clear the current ESP32, breadboard, switch/encoder and wiring
placeholders. This is not a verified complete hardware arrangement.

## Solder, wiring and service access

A 1 mm-thick rear solder keepout follows the actual source PCB outline. It
excludes the four intended contact lands (with 0.2 mm margins) and connector
region. The cradle base is 1.2 mm behind the PCB, leaving 0.2 mm additional
clearance beyond that assumed zone. The excluded contact lands must have no
components or unacceptable traces/solder; the model does not establish this.

A further 6 mm axial reserve behind the modeled connector includes 0.5 mm XY
allowance per side. No reserve collision was found. This does not model a real
wire bend, cable bundle, plug insertion sweep, connector pull load or strain
relief. Measure the assembled leads; enlarge reserves if necessary.

A provisional 4 mm diameter x 10 mm straight driver envelope is checked behind
the screw heads. Access to the lens-ring screws is blocked by the installed
cradle. This is handled by the adult service sequence, not ignored:

1. Disconnect all power and open the adult rear enclosure.
2. Disconnect the LCD leads without pulling on solder joints.
3. Remove the two PCB/cradle screws and the rear cradle. Support the LCD so it
   cannot fall, then withdraw it from behind. The lens remains separately held.
4. Only for lens replacement, remove the two ring screws and the retainer, then
   withdraw the lens inward. Reassemble the lens capture before reinstalling LCD.
5. Verify no glass pressure, free wiring, correct window alignment, and full
   fastener engagement without protrusion or excessive torque. Close the rear.

The existing full enclosure rear closure is still a concept, not a completed
secure access mechanism. No child should have access to any loose parts.

## Fit-test printing and acceptance

The independent test document contains a **64 x 68 x 5 mm** panel coupon with
5 mm plan corner radius and LCD axis at **(32,36)** mm. It reproduces both
standoffs, blind pilots, optical lip/pocket, shoulder pocket and header relief.
The SVG dimension drawing is generated from its parameter sheet; dimensions
ending TBD and fit allowances must be tested, not treated as manufacturing specs.

The three printable pieces are coupon, retainer and cradle. The polycarbonate
lens, LCD and screws are purchased components and are not printed. The native
PrintLayout group provides separate links with flat orientations; it spans about
189 x 68 mm before brim, spacing/keep-outs or printer constraints. Verify actual
slice bounds. Keep only that group visible for checking the print layout; it is
hidden by default so it does not overlap the assembled fit test. After parameter
changes, re-pack the print links and regenerate the drawing; reports are snapshots.

No printable STL has been exported. Inspect slicer behavior, particularly the
2.1 mm radial shoulder overhang, small bores, 1 mm nose wall, rail/pad junctions,
and layer orientation. Use a suitable material/process and adult fit-test loads;
no safe material or strength is inferred from the appearance. Do not sand or
force the actual LCD into a wrong fit. Check both boards, not only one sample.

Before a full enclosure print, record lens edge capture and axial stack, screw
fit/torque and durability, both PCB-hole fits, unsupported rear components,
header/solder/plug/wire clearance, display centering and viewing cone, and all
replacement steps. Strength, impact, lens retention, fastener accessibility,
small parts and child safety remain unqualified.

## Remaining physical measurements

1. Hole diameter/pitch/coordinates on both Dorhea boards, and the reported
   board-to-LCD center offset; capture method, readings and tolerances.
2. Actual PCB thickness and board-front/back to glass front, bezel and FPC.
   The source 0.41148 mm PCB value remains numerically unconfirmed.
3. Rear component/solder protrusions and clear contact lands at the two neck
   clamps and two backside pads, including electrical insulation needs.
4. Header front/rear heights, solder height, mating plug dimensions, lead exit,
   insertion/removal clearance and minimum bend radius.
5. Active diameter and position; actual lens diameter/thickness, cut edge finish,
   flatness and thermal behavior; assembled gap under allowable loads.
6. Selected screw type, actual head/shank/length, engagement requirements,
   pilot fit, driver access and torque; print tolerances and material strength.
7. Full rear access and retention, cable strain relief, battery/service layout
   consolidation and repeatable display replacement without front disassembly.

The geometry report separates intended PCB support and lens/panel contacts from
unintended volume intersections. Thread engagement of screw envelopes is not a
thread simulation. All earlier mechanical, electrical and material safety gates
remain in force; this design does not establish child-safe handling.
