"""FreeCAD MCP entry point. Reuse I01 construction recipe without editing I01."""
from pathlib import Path
import hashlib
root = Path(r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit\enclosure\freecad')
original = root / 'MyFirstQubit_enclosure_iteration01.FCStd'
before = hashlib.sha256(original.read_bytes()).hexdigest()
recipe = (root / 'create_iteration01.py').read_text()
recipe = recipe.replace('MyFirstQubit_Enclosure_I01','MyFirstQubit_Enclosure_I02')
recipe = recipe.replace('MyFirstQubit_enclosure_iteration01.FCStd','MyFirstQubit_enclosure_iteration02.FCStd')
recipe = recipe.replace("'LCDY':151", "'LCDY':158")
recipe = recipe.replace("'EncoderY':100, 'KnobDiameter':36", "'EncoderY':108, 'KnobDiameter':40")
recipe = recipe.replace("'GateY':57, 'GateHX':32, 'GateXX':80", "'GateY':64, 'GateHX':176, 'GateXX':32")
recipe = recipe.replace("'GateYX':128, 'GateZX':176", "'GateYX':80, 'GateZX':128")
recipe = recipe.replace("'ActionY':23, 'MeasureX':48, 'ResetX':104", "'ActionY':26, 'MeasureX':104, 'ResetX':40")
recipe = recipe.replace("'ColorsX':160, 'ButtonDiameter':26", "'ColorsX':168, 'ButtonDiameter':28")
recipe = recipe.replace("'RearClearanceTBD':1", "'RearClearanceTBD':1, 'MeasureDiameter':40, 'SecondaryDiameter':22, 'DisplaySurroundDiameter':42, 'SurroundHeight':1, 'LabelSize':4, 'GateLabelSize':6")
recipe = recipe.replace("cap=cyl(title+'ButtonConcept','ButtonDiameter/2'", "cap=cyl(title+'ButtonConcept',('MeasureDiameter/2' if title=='Measure' else 'SecondaryDiameter/2' if title in ('Reset','Colors') else 'ButtonDiameter/2')")
# Extend the native model before its sole save operation.
marker = "doc.saveAs(os.path.join(ROOT,'MyFirstQubit_enclosure_iteration02.FCStd'))"
extra = '''
import Draft
ux=doc.addObject('App::DocumentObjectGroup','PanelUX')
ux.Label='Display surrounds and visual label concepts - retention unresolved'
for side,x in [('Left','LCDLeftX'),('Right','LCDRightX')]:
    ringOuter=cyl(side+'SurroundOuter','DisplaySurroundDiameter/2','SurroundHeight',x,'LCDY',topZ)
    ringInner=cyl(side+'SurroundInner','LCDOpeningTBD/2','SurroundHeight+RearClearanceTBD',x,'LCDY',topZ)
    ring=doc.addObject('Part::Cut',side+'DisplaySurroundConcept'); ux.addObject(ring)
    ring.Base=ringOuter; ring.Tool=ringInner; ring.Refine=True
    ringOuter.Visibility=False; ringInner.Visibility=False
    ring.ViewObject.ShapeColor=(0.22,0.33,0.39)
doc.MeasureButtonConcept.ViewObject.ShapeColor=(0.94,0.48,0.13)
for name in ['Reset','Colors']:
    doc.getObject(name+'ButtonConcept').ViewObject.ShapeColor=(0.64,0.68,0.69)
for name in ['X','Y','Z','H']:
    doc.getObject(name+'ButtonConcept').ViewObject.ShapeColor=(0.38,0.63,0.65)
doc.recompute()
def label(name,text,x,y,z,size):
    s=Draft.make_shapestring(String=text,FontFile=r'C:\\Windows\\Fonts\\arial.ttf',Size=4,Tracking=0)
    s.Label=name+' - visual text concept'; ux.addObject(s)
    ex(s,'Size',size); doc.recompute()
    # Font-specific offset centers this initial label; text changes may require recentering.
    offset=s.Shape.BoundBox.XLength/2
    ex(s,'Placement.Base.x',x+'-'+str(offset)+' mm')
    ex(s,'Placement.Base.y',y); ex(s,'Placement.Base.z',z)
    s.ViewObject.ShapeColor=(0.12,0.16,0.18)
    return s
for title,x,y in buttons:
    label(title,title,x,y+'-2 mm',topZ+'+ButtonHeight+0.05 mm','GateLabelSize' if len(title)==1 else 'LabelSize')
label('ProbabilityLabel','PROBABILITY','LCDLeftX','EncoderY-28 mm',topZ+'+0.05 mm','LabelSize')
label('PhaseLabel','PHASE','LCDRightX','EncoderY-28 mm',topZ+'+0.05 mm','LabelSize')
label('ZeroLabel','|0>','LCDLeftX','LCDY+26 mm',topZ+'+0.05 mm','LabelSize')
label('OneLabel','|1>','LCDRightX','LCDY+26 mm',topZ+'+0.05 mm','LabelSize')
doc.recompute()
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
'''
recipe=recipe.replace(marker,extra+'\n'+marker)
exec(compile(recipe,str(root/'create_iteration01.py')+' (I02 recipe)','exec'))
view=Gui.activeDocument().activeView()
Gui.Selection.clearSelection()
view.setCameraType('Orthographic')
for name,rotation in [('top',App.Rotation(0,0,0,1)),('axonometric',App.Rotation(0.3647051996310009,0.2798481423331213,0.11591689595929514,0.8804762392171493))]:
    view.setCameraOrientation(rotation.Q); Gui.updateGui(); view.fitAll(); Gui.updateGui()
    view.saveImage(str(root/('iteration02-'+name+'.png')),1400,1200,'White')
assert hashlib.sha256(original.read_bytes()).hexdigest()==before, 'I01 changed unexpectedly'
print('Iteration01 SHA256 unchanged:',before)
items=doc.Housing.Group+doc.ElectronicsPlaceholders.Group
collisions=[]
for i,a in enumerate(items):
    for b in items[i+1:]:
        v=a.Shape.common(b.Shape).Volume
        if v>0.001: collisions.append((a.Name,b.Name,round(v,3)))
print('Housing/electronics interferences:',collisions)
print('Invalid objects:',[(o.Name,str(o.State)) for o in doc.Objects if 'Invalid' in o.State])
