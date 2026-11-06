"""Run inside FreeCAD GUI via MCP. Creates a new document; never edits meshes."""
import os
import Part

ROOT = r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit\enclosure\freecad'
doc = App.newDocument('MyFirstQubit_Enclosure_I01')
p = doc.addObject('Spreadsheet::Sheet', 'Parameters')
p.Label = 'Parameters - design choices and unverified TBD envelopes (mm)'
values = {
    'Width':208, 'Depth':198, 'CornerRadius':14, 'Wall':3, 'Floor':3,
    'BaseHeight':30, 'PanelThickness':3, 'JointGapTBD':0.3,
    'LCDLeftX':58, 'LCDRightX':150, 'LCDY':151, 'LCDOpeningTBD':34,
    'LCDEnvelopeWidthTBD':42, 'LCDEnvelopeDepthTBD':42, 'LCDEnvelopeHeightTBD':6,
    'EncoderY':100, 'KnobDiameter':36, 'KnobHeight':12,
    'ShaftOpeningTBD':9, 'EncoderWidthTBD':18, 'EncoderDepthTBD':18,
    'EncoderHeightTBD':14, 'GateY':57, 'GateHX':32, 'GateXX':80,
    'GateYX':128, 'GateZX':176, 'ActionY':23, 'MeasureX':48, 'ResetX':104,
    'ColorsX':160, 'ButtonDiameter':26, 'ButtonHeight':5,
    'ActuatorOpeningTBD':12, 'SwitchWidthTBD':8, 'SwitchDepthTBD':8,
    'SwitchHeightTBD':6, 'ESPWidthTBD':28, 'ESPDepthTBD':65,
    'ESPHeightTBD':14, 'ESPX':104, 'ESPY':150, 'ESPBottom':8,
    'BreadboardWidthTBD':165, 'BreadboardDepthTBD':55,
    'BreadboardHeightTBD':10, 'BreadboardX':104, 'BreadboardY':66,
    'BreadboardBottom':4, 'RearClearanceTBD':1
}
for row, (key, val) in enumerate(values.items(), 1):
    p.set('A'+str(row), key)
    p.set('B'+str(row), str(val)+' mm')
    p.setAlias('B'+str(row), key)
    p.set('C'+str(row), 'TBD: physical verification required' if key.endswith('TBD') else 'Proposed design choice')
p.setColumnWidth('A',220); p.setColumnWidth('B',100); p.setColumnWidth('C',310)
housing = doc.addObject('App::DocumentObjectGroup','Housing')
electronics = doc.addObject('App::DocumentObjectGroup','ElectronicsPlaceholders')
controls = doc.addObject('App::DocumentObjectGroup','ControlSurfaceConcepts')
construction = doc.addObject('App::DocumentObjectGroup','Construction')

def ex(obj, prop, expr):
    # All dimensional values are expressed through named spreadsheet parameters.
    import re
    expr = re.sub(r'\b('+'|'.join(sorted(values,key=len,reverse=True))+r')\b', r'Parameters.\1', expr)
    obj.setExpression(prop, expr)

def box(name,w,d,h,x,y,z, group=construction):
    o=doc.addObject('Part::Box',name); group.addObject(o)
    for prop,expr in [('Length',w),('Width',d),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]: ex(o,prop,expr)
    return o

def cyl(name,r,h,x,y,z,group=construction):
    o=doc.addObject('Part::Cylinder',name); group.addObject(o)
    for prop,expr in [('Radius',r),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]: ex(o,prop,expr)
    return o

def rounded(name,w,d,r,h,x,y,z):
    parts=[box(name+'WebX',f'({w})-2*({r})',d,h,f'({x})+({r})',y,z),
           box(name+'WebY',w,f'({d})-2*({r})',h,x,f'({y})+({r})',z)]
    for i,(xx,yy) in enumerate([(f'({x})+({r})',f'({y})+({r})'),(f'({x})+({w})-({r})',f'({y})+({r})'),(f'({x})+({r})',f'({y})+({d})-({r})'),(f'({x})+({w})-({r})',f'({y})+({d})-({r})')]):
        parts.append(cyl(name+'Corner'+str(i),r,h,xx,yy,z))
    o=doc.addObject('Part::MultiFuse',name); construction.addObject(o); o.Shapes=parts; o.Refine=True
    return o

outer=rounded('BaseOuter','Width','Depth','CornerRadius','BaseHeight','0 mm','0 mm','0 mm')
inner=rounded('CavityTool','Width-2*Wall','Depth-2*Wall','CornerRadius-Wall','BaseHeight','Wall','Wall','Floor')
base=doc.addObject('Part::Cut','BaseTray'); housing.addObject(base); base.Base=outer; base.Tool=inner; base.Refine=True
base.Label='Base tray - closure and mounts TBD'
panelZ='BaseHeight+JointGapTBD'
topZ=panelZ+'+PanelThickness'
blank=rounded('PanelBlank','Width','Depth','CornerRadius','PanelThickness','0 mm','0 mm',panelZ)
holes=[]
for side,x in [('Left','LCDLeftX'),('Right','LCDRightX')]:
    holes.append(cyl('LCD'+side+'Opening','LCDOpeningTBD/2','PanelThickness+2*RearClearanceTBD',x,'LCDY',panelZ+'-RearClearanceTBD'))
    lcd=box('LCD'+side+'BoardTBD','LCDEnvelopeWidthTBD','LCDEnvelopeDepthTBD','LCDEnvelopeHeightTBD',x+'-LCDEnvelopeWidthTBD/2','LCDY-LCDEnvelopeDepthTBD/2',panelZ+'-LCDEnvelopeHeightTBD-RearClearanceTBD',electronics)
    lcd.Label=side+' LCD board - TBD envelope'
for title,x in [('Probability','LCDLeftX'),('Phase','LCDRightX')]:
    holes.append(cyl(title+'ShaftTool','ShaftOpeningTBD/2','PanelThickness+2*RearClearanceTBD',x,'EncoderY',panelZ+'-RearClearanceTBD'))
    enc=box(title+'EncoderTBD','EncoderWidthTBD','EncoderDepthTBD','EncoderHeightTBD',x+'-EncoderWidthTBD/2','EncoderY-EncoderDepthTBD/2',panelZ+'-EncoderHeightTBD-RearClearanceTBD',electronics)
    enc.Label=title+' encoder - TBD envelope'
    knob=cyl(title+'KnobConcept','KnobDiameter/2','KnobHeight',x,'EncoderY',topZ,controls)
    knob.Label=title+' knob concept - no bore or retention'
buttons=[('H','GateHX','GateY'),('X','GateXX','GateY'),('Y','GateYX','GateY'),('Z','GateZX','GateY'),('Measure','MeasureX','ActionY'),('Reset','ResetX','ActionY'),('Colors','ColorsX','ActionY')]
for title,x,y in buttons:
    holes.append(cyl(title+'ActuatorTool','ActuatorOpeningTBD/2','PanelThickness+2*RearClearanceTBD',x,y,panelZ+'-RearClearanceTBD'))
    b=box(title+'SwitchTBD','SwitchWidthTBD','SwitchDepthTBD','SwitchHeightTBD',x+'-SwitchWidthTBD/2',y+'-SwitchDepthTBD/2',panelZ+'-SwitchHeightTBD-RearClearanceTBD',electronics)
    b.Label=title+' switch - TBD envelope'
    cap=cyl(title+'ButtonConcept','ButtonDiameter/2','ButtonHeight',x,y,topZ,controls)
    cap.Label=title+' button concept - guidance and retention TBD'
tool=doc.addObject('Part::MultiFuse','PanelOpeningTools'); construction.addObject(tool); tool.Shapes=holes
panel=doc.addObject('Part::Cut','FrontPanel'); housing.addObject(panel); panel.Base=blank; panel.Tool=tool; panel.Refine=True
panel.Label='Front panel - 2 LCD + 2 encoder + 7 button openings, all TBD'
esp=box('ESP32EnvelopeTBD','ESPWidthTBD','ESPDepthTBD','ESPHeightTBD','ESPX-ESPWidthTBD/2','ESPY-ESPDepthTBD/2','ESPBottom',electronics)
esp.Label='ESP32-S3 - TBD envelope, USB position unmodeled'
bb=box('BreadboardEnvelopeTBD','BreadboardWidthTBD','BreadboardDepthTBD','BreadboardHeightTBD','BreadboardX-BreadboardWidthTBD/2','BreadboardY-BreadboardDepthTBD/2','BreadboardBottom',electronics)
bb.Label='Breadboard - TBD planning envelope, not measured assembly'
doc.recompute()
for o in construction.Group: o.Visibility=False
for o in housing.Group:
    o.Visibility=True; o.ViewObject.ShapeColor=(0.79,0.84,0.86)
panel.ViewObject.ShapeColor=(0.91,0.87,0.76)
for o in electronics.Group:
    o.Visibility=False; o.ViewObject.ShapeColor=(0.18,0.58,0.39); o.ViewObject.Transparency=45
for i,o in enumerate(controls.Group):
    o.Visibility=True; o.ViewObject.ShapeColor=[(0.32,0.60,0.75),(0.81,0.53,0.33),(0.52,0.68,0.44),(0.72,0.49,0.60)][i%4]
doc.recompute()
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
doc.recompute()
doc.saveAs(os.path.join(ROOT,'MyFirstQubit_enclosure_iteration01.FCStd'))
print('SAVED',doc.FileName)
for o in [base,panel]+electronics.Group+controls.Group:
    print(o.Name, 'valid=',o.Shape.isValid(),'solids=',len(o.Shape.Solids),'bbox=',o.Shape.BoundBox)
print('Housing tree:',[o.Name for o in housing.Group])
print('Electronics tree:',[o.Name for o in electronics.Group])
print('Controls tree:',[o.Name for o in controls.Group])
