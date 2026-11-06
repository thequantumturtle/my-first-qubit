"""Run through FreeCAD MCP; preserve I01-I03, clone I03 for battery packaging."""
from pathlib import Path
import hashlib,json,csv
import Part
root=Path(r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit\enclosure\freecad')
source=root/'MyFirstQubit_enclosure_iteration03.FCStd'
target=root/'MyFirstQubit_enclosure_v04_battery_proposal.FCStd'
if target.exists():raise RuntimeError('Refusing to overwrite an existing proposal')
protected=[root/('MyFirstQubit_enclosure_iteration'+n+'.FCStd') for n in ['01','02','03']]
hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in protected}
src=next((d for d in App.listDocuments().values() if d.FileName==str(source)),None)
if src is None:src=App.openDocument(str(source))
src.saveCopy(str(target))
doc=App.openDocument(str(target));doc.Label='My First Qubit V0.4 - provisional battery packaging'
p=doc.addObject('Spreadsheet::Sheet','BatteryParameters')
p.Label='Battery packaging - unverified envelopes, no selected components'
values={'BatteryLayerDepth':26,'BatteryCoverThickness':3,'BatteryWidthTBD':70,
 'BatteryDepthTBD':65,'BatteryHeightTBD':20,'BatteryX':104,'BatteryY':99,
 'BatteryBottomClearanceTBD':1,'RegulatorWidthTBD':35,'RegulatorDepthTBD':25,
 'RegulatorHeightTBD':12,'RegulatorX':164,'RegulatorY':99,
 'ProtectionWidthTBD':20,'ProtectionDepthTBD':20,'ProtectionHeightTBD':10,
 'ProtectionX':44,'ProtectionY':99,'SwitchWidthTBD':25,'SwitchDepthTBD':15,
 'SwitchHeightTBD':12,'SwitchX':104,'SwitchY':150,
 'MonitorWidthTBD':20,'MonitorDepthTBD':15,'MonitorHeightTBD':8,
 'MonitorX':164,'MonitorY':135,'ModuleBottomClearanceTBD':3}
for row,(key,val) in enumerate(values.items(),1):
 p.set('A'+str(row),key);p.set('B'+str(row),str(val)+' mm');p.setAlias('B'+str(row),key)
 p.set('C'+str(row),'TBD: no verified component; planning allowance' if key.endswith('TBD') else 'Proposed packaging choice')
p.setColumnWidth('A',260);p.setColumnWidth('B',90);p.setColumnWidth('C',340)
parts=doc.addObject('App::DocumentObjectGroup','BatteryPowerProposal')
tools=doc.addObject('App::DocumentObjectGroup','BatteryConstruction')

def expr(o,prop,s):o.setExpression(prop,s)
def box(name,w,d,h,x,y,z,group=tools):
 o=doc.addObject('Part::Box',name);group.addObject(o)
 for key,value in [('Length',w),('Width',d),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:expr(o,key,value)
 return o
def cylinder(name,r,h,x,y,z):
 o=doc.addObject('Part::Cylinder',name);tools.addObject(o)
 for key,value in [('Radius',r),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:expr(o,key,value)
 return o
def rounded(name,w,d,r,h,x,y,z):
 members=[box(name+'X',f'({w})-2*({r})',d,h,f'({x})+({r})',y,z),box(name+'Y',w,f'({d})-2*({r})',h,x,f'({y})+({r})',z)]
 for i,(xx,yy) in enumerate([(f'({x})+({r})',f'({y})+({r})'),(f'({x})+({w})-({r})',f'({y})+({r})'),(f'({x})+({r})',f'({y})+({d})-({r})'),(f'({x})+({w})-({r})',f'({y})+({d})-({r})')]):
  members.append(cylinder(name+'C'+str(i),r,h,xx,yy,z))
 o=doc.addObject('Part::MultiFuse',name);tools.addObject(o);o.Shapes=members;o.Refine=True
 return o
B='BatteryParameters.';P='Parameters.'
bottom='-'+B+'BatteryLayerDepth'
coverTop=bottom+'+'+B+'BatteryCoverThickness'
outer=rounded('LowerLayerOuter',P+'Width',P+'Depth',P+'CornerRadius',B+'BatteryLayerDepth-'+B+'BatteryCoverThickness','0 mm','0 mm',coverTop)
inner=rounded('LowerLayerInner',P+'Width-2*'+P+'Wall',P+'Depth-2*'+P+'Wall',P+'CornerRadius-'+P+'Wall',B+'BatteryLayerDepth',P+'Wall',P+'Wall',coverTop)
walls=doc.addObject('Part::Cut','BatteryLayerWalls');parts.addObject(walls);walls.Base=outer;walls.Tool=inner;walls.Refine=True
walls.Label='Lower battery layer - joint and secure attachment unresolved'
cover=rounded('UndersideBatteryCover',P+'Width',P+'Depth',P+'CornerRadius',B+'BatteryCoverThickness','0 mm','0 mm',bottom)
tools.removeObject(cover);parts.addObject(cover)
cover.Label='Underside cover - REQUIRE screw security; fasteners/capture not modeled'
for o in [walls,cover]:
 o.addProperty('App::PropertyString','SecurityStatus');o.SecurityStatus='Not secured. Screw-secured adult-only access and captive-fastener design required before use.'

def envelope(name,prefix,x,y,z):
 o=box(name,B+prefix+'WidthTBD',B+prefix+'DepthTBD',B+prefix+'HeightTBD',B+x+'-'+B+prefix+'WidthTBD/2',B+y+'-'+B+prefix+'DepthTBD/2',z,parts)
 o.addProperty('App::PropertyString','Verification');o.Verification='UNVERIFIED planning envelope, NOT selected hardware dimensions. No mounting features authorized.'
 return o
holder=envelope('FourAANiMHHolderEnvelopeTBD','Battery','BatteryX','BatteryY',coverTop+'+'+B+'BatteryBottomClearanceTBD')
holder.Label='4x AA NiMH + purchased holder - total loaded envelope TBD'
reg=envelope('RegulatorEnvelopeTBD','Regulator','RegulatorX','RegulatorY',coverTop+'+'+B+'ModuleBottomClearanceTBD')
reg.Label='Regulator module reserve - topology/ratings/thermal clearance TBD'
protect=envelope('PowerProtectionEnvelopeTBD','Protection','ProtectionX','ProtectionY',coverTop+'+'+B+'ModuleBottomClearanceTBD')
switch=envelope('PhysicalOnOffSwitchEnvelopeTBD','Switch','SwitchX','SwitchY',coverTop+'+'+B+'ModuleBottomClearanceTBD')
switch.Label='Physical on/off switch reserve - adult service access; actuation TBD'
monitor=envelope('VoltageMonitorEnvelopeTBD','Monitor','MonitorX','MonitorY',coverTop+'+'+B+'ModuleBottomClearanceTBD')
monitor.Label='Voltage sensing reserve - circuitry/GPIO/cutoff not selected'
doc.recompute()
for o in tools.Group:o.Visibility=False
for o in parts.Group:
 o.Visibility=True;o.ViewObject.ShapeColor=(0.86,0.81,0.70) if o in [walls,cover] else (0.48,0.57,0.45)
 mat=o.ViewObject.ShapeAppearance[0];mat.SpecularColor=(0,0,0);mat.Shininess=0.1;o.ViewObject.ShapeAppearance=[mat]
 if o not in [walls,cover]:o.Visibility=False
doc.recompute()
existing=[doc.FrontHousingRounded,doc.RearTrayRounded]+list(doc.DiscoveryControls.Group)+list(doc.ElectronicsPlaceholders.Group)+list(doc.ProtectedDisplays.Group)
final=existing+list(parts.Group)
with (root/'v04-mass-worksheet.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['object','mass_g_MEASURE_REQUIRED','CAD_centroid_x_mm','CAD_centroid_y_mm','CAD_centroid_z_mm','status'])
 for o in final:
  if o.Name=='WiringReserveTBD':continue
  c=o.Shape.Solids[0].CenterOfMass
  w.writerow([o.Name,'',round(c.x,3),round(c.y,3),round(c.z,3),'CAD geometry/envelope centroid only; verify actual mass and mass centroid'])
 w.writerow(['Wiring fasteners and unmodeled attachments','','','','','Include actual masses/positions; do not count planning reserves as physical modules'])
results={'invalid':[],'intersections':[],'preserved_sha256':hashes,
 'dimensions_mm':{'footprint':[208,198],'original_housing_height':35.3,'proposed_housing_height':61.3,'increase':26,'including_knobs':75.3},
 'measurements_status':'Holder not selected/verified; currents and component masses NOT measured; no actual COM or runtime claim.'}
for o in final:
 if not o.Shape.isValid() or len(o.Shape.Solids)!=1:results['invalid'].append(o.Name)
for i,a in enumerate(final):
 for b in final[i+1:]:
  v=a.Shape.common(b.Shape).Volume
  if v>0.001:results['intersections'].append([a.Name,b.Name,round(v,5)])
results['holder_gaps_mm']={'ceiling':-holder.Shape.BoundBox.ZMax,'cover':holder.Shape.BoundBox.ZMin-cover.Shape.BoundBox.ZMax,
 'regulator':holder.Shape.distToShape(reg.Shape)[0],'protection':holder.Shape.distToShape(protect.Shape)[0]}
results['battery_envelope_centroid_mm']=[holder.Shape.CenterOfMass.x,holder.Shape.CenterOfMass.y,holder.Shape.CenterOfMass.z]
print(json.dumps(results,indent=2))
from pivy import coin
v=Gui.activeDocument().activeView();v.setCameraType('Orthographic');Gui.Selection.clearSelection()
def shot(name,q):
 v.getCameraNode().orientation.setValue(coin.SbRotation(*q));Gui.updateGui();v.fitAll();Gui.updateGui()
 v.saveImage(str(root/name),1500,1200,'White')
shot('v04-battery-exterior.png',(0.3647051996310009,0.2798481423331213,0.11591689595929514,0.8804762392171493))
cover.Visibility=False
for o in [holder,reg,protect,switch,monitor]:o.Visibility=True
shot('v04-battery-underside-open.png',(1,0,0,0))
for o in [holder,reg,protect,switch,monitor]:o.Visibility=False
cover.Visibility=True
v.getCameraNode().orientation.setValue(coin.SbRotation(0.3647051996310009,0.2798481423331213,0.11591689595929514,0.8804762392171493));Gui.updateGui();v.fitAll();Gui.updateGui()
settings=App.ParamGet('User parameter:BaseApp/Preferences/Document');old=settings.GetInt('CountBackupFiles',1);settings.SetInt('CountBackupFiles',0)
try:doc.recompute();doc.save()
finally:settings.SetInt('CountBackupFiles',old)
for f in protected:assert hashlib.sha256(f.read_bytes()).hexdigest()==hashes[str(f)]
(root/'v04-battery-validation.json').write_text(json.dumps(results,indent=2))
print('Saved',target)
