"""Execute via FreeCAD MCP. New native I03; earlier files are read-only inputs."""
from pathlib import Path
import hashlib
import math
import csv
import json
import Part
root=Path(r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit\enclosure\freecad')
protected=[root/('MyFirstQubit_enclosure_iteration'+n+'.FCStd') for n in ['01','02']]
hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in protected}
target=root/'MyFirstQubit_enclosure_iteration03.FCStd'
if target.exists():
    raise RuntimeError('Iteration 03 already exists; refusing to overwrite')
recipe=(root/'create_iteration01.py').read_text()
replacements={
 'MyFirstQubit_Enclosure_I01':'MyFirstQubit_Enclosure_I03',
 'MyFirstQubit_enclosure_iteration01.FCStd':'MyFirstQubit_enclosure_iteration03.FCStd',
 "'CornerRadius':14":"'CornerRadius':20",
 "'PanelThickness':3":"'PanelThickness':5",
 "'LCDY':151":"'LCDY':158",
 "'EncoderY':100, 'KnobDiameter':36, 'KnobHeight':12":"'EncoderY':108, 'KnobDiameter':40, 'KnobHeight':14",
 "'GateY':57, 'GateHX':32, 'GateXX':80":"'GateY':65, 'GateHX':176, 'GateXX':32",
 "'GateYX':128, 'GateZX':176":"'GateYX':80, 'GateZX':128",
 "'ActionY':23, 'MeasureX':48, 'ResetX':104":"'ActionY':28, 'MeasureX':104, 'ResetX':40",
 "'ColorsX':160, 'ButtonDiameter':26, 'ButtonHeight':5":"'ColorsX':168, 'ButtonDiameter':28, 'ButtonHeight':6",
 "panelZ+'-LCDEnvelopeHeightTBD-RearClearanceTBD'":"panelZ+'-LCDEnvelopeHeightTBD-LCDBoardSetbackTBD'",
 "cap=cyl(title+'ButtonConcept','ButtonDiameter/2','ButtonHeight'":"cap=cyl(title+'ButtonConcept',('MeasureDiameter/2' if title=='Measure' else 'SecondaryDiameter/2' if title in ('Reset','Colors') else 'ButtonDiameter/2'),('SecondaryHeight' if title in ('Reset','Colors') else 'ButtonHeight')"
}
for old,new in replacements.items():
    assert old in recipe, old
    recipe=recipe.replace(old,new)
more={'MeasureDiameter':36,'SecondaryDiameter':22,'SecondaryHeight':4,
      'KnobRounding':6,'ButtonRounding':4,'SecondaryRounding':2.5,
      'HousingRounding':1.2,'LensDiameterTBD':38,'LensThicknessTBD':1.5,
      'LensRadialClearanceTBD':0.3,'LensRecess':1,'RetainerOuterDiameter':44,
      'RetainerNoseDiameterTBD':38.4,'RetainerFlangeThickness':2,
      'RetainerNoseHeight':2.5,'LCDBoardSetbackTBD':4,
      'ActiveProxyHeightTBD':1,'WiringReserveWidthTBD':72,'WiringReserveDepthTBD':14,
      'WiringReserveHeightTBD':12,'WiringReserveX':104,'WiringReserveY':102,
      'WiringReserveBottom':4}
recipe=recipe.replace("'RearClearanceTBD':1", "'RearClearanceTBD':1,"+','.join(repr(k)+':'+str(v) for k,v in more.items()))
# Stop before the I01 recipe's save and diagnostic output; complete I03 first.
recipe=recipe[:recipe.index("doc.saveAs(")]
exec(compile(recipe,'I03 native base construction','exec'))
# Maintain the lens sandwich when thickness/recess parameters change.
for row,key in enumerate(values,1):
    if key=='RetainerNoseHeight': p.set('B'+str(row),'=PanelThickness-LensRecess-LensThicknessTBD')
cream=(0.86,0.81,0.70); sage=(0.47,0.58,0.45); blue=(0.44,0.56,0.62)
terra=(0.65,0.43,0.34); ochre=(0.70,0.58,0.34)

def finish(o,color,transparency=0):
    o.ViewObject.ShapeColor=color; o.ViewObject.LineColor=tuple(c*0.65 for c in color)
    o.ViewObject.DisplayMode='Flat Lines'; o.ViewObject.Transparency=transparency
    material=o.ViewObject.ShapeAppearance[0]
    material.DiffuseColor=color; material.Shininess=0.1
    material.SpecularColor=(0.0,0.0,0.0)
    o.ViewObject.ShapeAppearance=[material]

def rounded_top(source,name,radius,group,outer_only=False,bottom=False):
    doc.recompute()
    z=source.Shape.BoundBox.ZMin if bottom else source.Shape.BoundBox.ZMax
    edges=[]
    for i,e in enumerate(source.Shape.Edges,1):
        b=e.BoundBox
        if abs(b.ZMin-z)<1e-5 and abs(b.ZMax-z)<1e-5:
            if not outer_only or min(b.XMin,b.YMin)<0.01 or b.XMax>207.99 or b.YMax>197.99:
                edges.append('Edge'+str(i))
    body=doc.addObject('PartDesign::Body',name); group.addObject(body)
    body.BaseFeature=source; doc.recompute()
    # Primitive BaseFeatures are local to the Body; preserve their parametric
    # world placement explicitly. Boolean housing shapes already carry theirs.
    if source.TypeId=='Part::Cylinder':
        for axis in ['x','y','z']:
            body.setExpression('Placement.Base.'+axis,source.Name+'.Placement.Base.'+axis)
    fillet=body.newObject('PartDesign::Fillet',name+'Rim')
    fillet.Base=(body.Group[0],edges); ex(fillet,'Radius',radius)
    doc.recompute()
    if fillet.Shape.isNull() or not fillet.Shape.isValid(): raise RuntimeError('Fillet failed: '+name)
    source.Visibility=False; body.Group[0].Visibility=False; body.Visibility=True
    return body

ux=doc.addObject('App::DocumentObjectGroup','DiscoveryControls')
ux.Label='Rounded control concepts - attachment unresolved'
for source in list(controls.Group):
    secondary=source.Name.startswith(('Reset','Colors'))
    knob='Knob' in source.Name
    radius='KnobRounding' if knob else 'SecondaryRounding' if secondary else 'ButtonRounding'
    body=rounded_top(source,source.Name+'Rounded',radius,ux)
    body.Label=source.Label.replace('concept','rounded concept')
    color=sage if source.Name.startswith(('Probability','X','H')) else blue if source.Name.startswith(('Phase','Y')) else terra if source.Name.startswith('Z') else ochre if source.Name.startswith('Measure') else cream
    finish(body.Tip,color); finish(body,color)
    source.Visibility=False
controls.Label='Underlying control envelopes - hidden; see DiscoveryControls'

lcds=doc.addObject('App::DocumentObjectGroup','ProtectedDisplays')
lcds.Label='Polycarbonate lenses and internal stepped retainers - provisional'
lensBottom=topZ+'-LensRecess-LensThicknessTBD'
lipUnder=topZ+'-LensRecess'
ringTop=lensBottom
flangeTop=panelZ
flangeBottom=panelZ+'-RetainerFlangeThickness'
pockets=[]
for side,x in [('Left','LCDLeftX'),('Right','LCDRightX')]:
    pocket=cyl(side+'LensPocketTool','LensDiameterTBD/2+LensRadialClearanceTBD',
               'PanelThickness-LensRecess+RearClearanceTBD',x,'LCDY',panelZ+'-RearClearanceTBD')
    pockets.append(pocket)
    lens=cyl(side+'PolycarbonateLensTBD','LensDiameterTBD/2','LensThicknessTBD',x,'LCDY',lensBottom,lcds)
    lens.Label=side+' clear polycarbonate lens - 1.5 mm provisional'
    lens.addProperty('App::PropertyString','MaterialNote'); lens.MaterialNote='Clear polycarbonate, separately sourced; not opaque printed plastic. Grade/impact performance TBD.'
    finish(lens,(0.72,0.85,0.88),78)
    flange=cyl(side+'RetainerFlangeBlank','RetainerOuterDiameter/2','RetainerFlangeThickness',x,'LCDY',flangeBottom)
    nose=cyl(side+'RetainerNoseBlank','RetainerNoseDiameterTBD/2','RetainerNoseHeight',x,'LCDY',flangeTop)
    united=doc.addObject('Part::Fuse',side+'SteppedRetainerBlank'); construction.addObject(united); united.Base=flange; united.Tool=nose; united.Refine=True
    bore=cyl(side+'RetainerBoreTool','LCDOpeningTBD/2','RetainerFlangeThickness+RetainerNoseHeight+2*RearClearanceTBD',x,'LCDY',flangeBottom+'-RearClearanceTBD')
    ring=doc.addObject('Part::Cut',side+'LensRetainerTBD'); lcds.addObject(ring); ring.Base=united; ring.Tool=bore; ring.Refine=True
    ring.Label=side+' internal lens retainer - attachment TBD'; finish(ring,cream)
    active=cyl(side+'ActiveDisplayProxyTBD','LCDOpeningTBD/2','ActiveProxyHeightTBD',x,'LCDY',panelZ+'-LCDBoardSetbackTBD',lcds)
    active.Label=side+' LCD active-surface proxy - location and diameter TBD'
    finish(active,sage if side=='Left' else blue)
    # Small visible probability disks are static CAD illustrations, not electronics changes.
    lens.Visibility=True; ring.Visibility=False; active.Visibility=True
tools=doc.addObject('Part::MultiFuse','LensPocketTools'); construction.addObject(tools); tools.Shapes=pockets
pocketed=doc.addObject('Part::Cut','PocketedFrontPanel'); construction.addObject(pocketed); pocketed.Base=panel; pocketed.Tool=tools; pocketed.Refine=True
doc.recompute()
panel.Visibility=False; base.Visibility=False
front=rounded_top(pocketed,'FrontHousingRounded','HousingRounding',housing,True)
front.Label='Warm cream front housing - inner lip captures lens from front'
rear=rounded_top(base,'RearTrayRounded','HousingRounding',housing,True,True)
rear.Label='Removable rear tray concept - rear closure/fasteners TBD'
for o in [front,rear]: finish(o,cream); finish(o.Tip,cream)
reserve=box('WiringReserveTBD','WiringReserveWidthTBD','WiringReserveDepthTBD','WiringReserveHeightTBD','WiringReserveX-WiringReserveWidthTBD/2','WiringReserveY-WiringReserveDepthTBD/2','WiringReserveBottom',electronics)
reserve.Label='Wiring reserve only - not a routed harness'; reserve.Visibility=False
doc.recompute()
for o in construction.Group: o.Visibility=False
for o in electronics.Group: o.Visibility=False
for o in controls.Group: o.Visibility=False
base.Visibility=False; panel.Visibility=False
front.Visibility=True;rear.Visibility=True

# Quantitative validation of actual I03 components (exclude hidden boolean tools).
assembled=[front,rear]+list(ux.Group)+list(electronics.Group)+list(lcds.Group)
validation={'invalid':[],'intersections':[],'contacts':[], 'preserved_sha256':hashes}
for o in assembled:
    if o.Shape.isNull() or not o.Shape.isValid() or len(o.Shape.Solids)!=1:
        validation['invalid'].append(o.Name)
for i,a in enumerate(assembled):
    for b in assembled[i+1:]:
        v=a.Shape.common(b.Shape).Volume
        if v>0.001: validation['intersections'].append([a.Name,b.Name,round(v,5)])
        else:
            dist=a.Shape.distToShape(b.Shape)[0]
            if dist<0.0001: validation['contacts'].append([a.Name,b.Name])
layout=[('LeftLCDcapture',58,158,44),('RightLCDcapture',150,158,44),('Probability',58,108,40),('Phase',150,108,40),('X',32,65,28),('Y',80,65,28),('Z',128,65,28),('H',176,65,28),('Reset',40,28,22),('Measure',104,28,36),('Colors',168,28,22)]
with (root/'iteration03-clearances.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['A','B','center_distance_mm','envelope_gap_mm'])
    for i,(a,x,y,da) in enumerate(layout):
        for b,xx,yy,db in layout[i+1:]:
            c=math.hypot(x-xx,y-yy);w.writerow([a,b,round(c,4),round(c-(da+db)/2,4)])
view=Gui.activeDocument().activeView();Gui.Selection.clearSelection()
view.setCameraType('Orthographic')
ax=App.Rotation(0.3647051996310009,0.2798481423331213,0.11591689595929514,0.8804762392171493)
def screenshot(view,path,rot):
    from pivy import coin
    view.getCameraNode().orientation.setValue(coin.SbRotation(*rot.Q))
    Gui.updateGui();view.fitAll();Gui.updateGui()
    view.saveImage(str(path),1500,1300,'White')
screenshot(view,root/'iteration03-top.png',App.Rotation(0,0,0,1))
screenshot(view,root/'iteration03-axonometric.png',ax)
doc.recompute();doc.saveAs(str(target))

# Exploded visualization uses disposable copies, leaving assembly placements unchanged.
exploded=App.newDocument('I03_Lens_Exploded_Review')
center=App.Vector(58,158,0)
crop=Part.makeCylinder(26,60,App.Vector(58,158,0))
parts=[('Front lip and pocket (local cutaway)',front.Shape.common(crop),20,cream,0),
       ('Clear polycarbonate lens 1.5 mm',doc.LeftPolycarbonateLensTBD.Shape,8,(0.72,0.85,0.88),55),
       ('Internal stepped retainer - attachment TBD',doc.LeftLensRetainerTBD.Shape,-8,cream,0),
       ('LCD active surface proxy',doc.LeftActiveDisplayProxyTBD.Shape,-20,sage,0),
       ('LCD PCB envelope',doc.LCDLeftBoardTBD.Shape,-20,(0.28,0.40,0.32),0)]
for i,(label,shape,offset,color,alpha) in enumerate(parts):
    o=exploded.addObject('Part::Feature','ExplodedPart'+str(i));o.Label=label
    s=shape.copy();s.translate(App.Vector(-58,-158,offset));o.Shape=s;finish(o,color,alpha)
exploded.recompute()
screenshot(Gui.activeDocument().activeView(),root/'iteration03-lcd-exploded.png',ax)
App.closeDocument(exploded.Name);App.setActiveDocument(doc.Name)
Gui.activeDocument().activeView().setCameraOrientation(ax.Q);Gui.activeDocument().activeView().fitAll();Gui.updateGui()
for f in protected: assert hashlib.sha256(f.read_bytes()).hexdigest()==hashes[str(f)],'Earlier design changed'
(root/'iteration03-validation.json').write_text(json.dumps(validation,indent=2))
print(json.dumps(validation,indent=2))
print('Saved',target)
