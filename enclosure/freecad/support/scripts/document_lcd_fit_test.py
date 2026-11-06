"""Generate a dimensioned vector reference directly from the native fit parameters."""
from pathlib import Path
import math
root=Path(r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit\enclosure\freecad')
fit=next((d for d in App.listDocuments().values() if d.FileName.endswith('MyFirstQubit_LCD_fit_test.FCStd')),None)
if fit is None:fit=App.openDocument(str(root/'MyFirstQubit_LCD_fit_test.FCStd'))
p=fit.LCDMountParameters
def mm(k):return p.get(k).Value
W,H=mm('CouponWidth'),mm('CouponDepth');cx,cy=mm('CouponCenterX'),mm('CouponCenterY')
def X(x):return 85+6*x
def Y(y):return 665-6*y
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="280mm" height="210mm" viewBox="0 0 1120 840">',
 '<defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#46594e"/></marker></defs>',
 '<rect width="1120" height="840" fill="white"/>',
 '<style>text{font-family:Arial,sans-serif;fill:#24382b} .dim{stroke:#46594e;stroke-width:1;fill:none;marker-start:url(#arr);marker-end:url(#arr)} .ext{stroke:#859389;stroke-width:1} .hidden{fill:none;stroke:#6f8276;stroke-width:1.3;stroke-dasharray:5 4}</style>']
def text(x,y,s,size=15):svg.append(f'<text x="{x}" y="{y}" font-size="{size}">{s}</text>')
def line(x1,y1,x2,y2,cls='ext'):svg.append(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
def circle(x,y,d,cls='hidden'):
 svg.append(f'<circle class="{cls}" cx="{X(x)}" cy="{Y(y)}" r="{3*d}"/>')
text(40,45,'MY FIRST QUBIT / LCD FIT TEST',25)
text(40,73,'Prototype dimensional reference | mm | read dimensions, do not scale | front view with hidden rear features')
svg.append(f'<rect x="{X(0)}" y="{Y(H)}" width="{6*W}" height="{6*H}" rx="{6*mm("CouponCornerRadius")}" fill="#eee8d7" stroke="#364e40" stroke-width="2"/>')
circle(cx,cy,mm('ApertureDiameterTBD'),'aperture')
svg.append(f'<style>.aperture{{fill:white;stroke:#364e40;stroke-width:2}}</style>')
circle(cx,cy,mm('LensPocketDiameterTBD'));circle(cx,cy,mm('ShoulderPocketDiameter'))
line(X(cx)-12,Y(cy),X(cx)+12,Y(cy));line(X(cx),Y(cy)-12,X(cx),Y(cy)+12)
holeY=cy+mm('SourceHoleY');holeXs=[cx+mm('HoleLeftX'),cx+mm('HoleRightX')]
for x in holeXs:
 circle(x,holeY,mm('PCBPostDiameter'));circle(x,holeY,mm('PilotDiameterTBD'))
 line(X(x)-6,Y(holeY),X(x)+6,Y(holeY));line(X(x),Y(holeY)-6,X(x),Y(holeY)+6)
for x in [cx-mm('LensScrewX'),cx+mm('LensScrewX')]:circle(x,cy,mm('PilotDiameterTBD'))
rx=cx+mm('SourceHeaderCenterX')-mm('HeaderReliefWidthTBD')/2
ry=cy+mm('SourceHeaderCenterY')+mm('HeaderReliefDepthTBD')/2
svg.append(f'<rect class="hidden" x="{X(rx)}" y="{Y(ry)}" width="{6*mm("HeaderReliefWidthTBD")}" height="{6*mm("HeaderReliefDepthTBD")}"/>')
# Overall width/depth and reference origins.
line(X(0),Y(0)+35,X(W),Y(0)+35,'dim');text(X(W/2)-12,Y(0)+59,f'{W:g}')
for x in [0,W]:line(X(x),Y(0)+2,X(x),Y(0)+40)
line(X(0)-35,Y(0),X(0)-35,Y(H),'dim');text(X(0)-66,Y(H/2),f'{H:g}')
for y in [0,H]:line(X(0)-40,Y(y),X(0)-2,Y(y))
# Hole pitch and axis-to-hole-row dimensions.
line(X(holeXs[0]),Y(holeY)+37,X(holeXs[1]),Y(holeY)+37,'dim')
text(X(cx)-12,Y(holeY)+58,f'{mm("SourceHolePitch"):g}')
for x in holeXs:line(X(x),Y(holeY)+4,X(x),Y(holeY)+41)
line(X(W)+32,Y(cy),X(W)+32,Y(holeY),'dim');text(X(W)+40,Y((cy+holeY)/2),f'{-mm("SourceHoleY"):.3f}')
line(X(W)+27,Y(cy),X(W)+38,Y(cy));line(X(W)+27,Y(holeY),X(W)+38,Y(holeY))
text(X(0),Y(H)-19,'C: LCD axis; lower-left corner is (0,0)')
text(565,120,'PANEL / MODEL-DERIVED LOCATION',19)
notes=[
 f'Panel: {W:g} x {H:g} x {mm("PanelThickness"):g}; plan corners R{mm("CouponCornerRadius"):g}.',
 f'LCD axis C = ({cx:g}, {cy:g}). Front +Z; rear features dashed.',
 f'Optical opening diameter {mm("ApertureDiameterTBD"):g} (active-area check pending).',
 f'Lens seat diameter {mm("LensPocketDiameterTBD"):g}; front lip {mm("LensRecess"):g} deep.',
 f'Lens: clear PC diameter {mm("LensDiameterTBD"):g} x {mm("LensThicknessTBD"):g}; separately sourced.',
 f'Rear shoulder pocket diameter {mm("ShoulderPocketDiameter"):g}, depth {mm("ShoulderThickness"):g}.',
 f'Modeled PCB holes: ({holeXs[0]:.3f}, {holeY:.3f}),',
 f'                              ({holeXs[1]:.3f}, {holeY:.3f}); pitch {mm("SourceHolePitch"):g}.',
 'Numerical hole/PCB dimensions are source values, not caliper records.',
 f'2 posts diameter {mm("PCBPostDiameter"):g}; blind pilot diameter {mm("PilotDiameterTBD"):g} x {mm("PCBPilotDepthTBD"):g}.',
 f'2 lens-ring pilots: ({cx-mm("LensScrewX"):g},{cy:g}), ({cx+mm("LensScrewX"):g},{cy:g});',
 f'  diameter {mm("PilotDiameterTBD"):g} x {mm("LensPilotDepthTBD"):g}, from rear; NOT through front.',
 f'Header relief {mm("HeaderReliefWidthTBD"):g} x {mm("HeaderReliefDepthTBD"):g} x {mm("HeaderReliefHeightTBD"):g} deep from rear.',
 f'Display-to-lens air gap target {mm("LensGapTargetTBD"):g}; test under load.',
 f'Cradle base {mm("BracketThickness"):g} thick, {mm("BracketRearGapTBD"):g} rear gap, four contact lands.',
 f'Retainer nose OD {mm("NoseOuterDiameterTBD"):g} / ID {mm("OpticalBoreDiameter"):g}.',
 'Thread-forming M2 screw/pilot assumptions REQUIRE fit testing.',
 'Do not force screws or bend the PCB. Front surface has no screws.'
]
for i,n in enumerate(notes):text(565,150+25*i,n,14)
text(40,758,'Print test only: panel + ring + cradle. LCD, clear lens and fasteners are purchased parts.',17)
text(40,785,'Confirm fit, lens capture, running clearances, strength and service access. NOT a child-safety approval.',16)
text(40,813,'Generated from LCDMountParameters; regenerate after edits. No general manufacturing tolerances are assigned.',14)
svg.append('</svg>')
(root/'LCD-fit-test-dimensions.svg').write_text('\n'.join(svg))
print('Saved dimensioned SVG',root/'LCD-fit-test-dimensions.svg')
