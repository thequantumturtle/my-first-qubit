"""FreeCAD MCP entry point. New provisional drawing-based revision; no STL export.

Reuses the historical construction functions without executing their old outputs.
All original CAD, firmware, vendor references and STL bytes are hash protected.
"""
from pathlib import Path
import hashlib, json, re
import Part
from pivy import coin

root=Path(globals().get('MFQ_REPO_ROOT',r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit'))
cad=root/'enclosure/freecad'
library=root/'hardware/models/gc9a01-meta-mcu'
componentFile=library/'GC9A01_drawing_PCB160_provisional.FCStd'
assemblyFile=cad/'MyFirstQubit_iteration03_LCD_PCB160.FCStd'
fitFile=cad/'MyFirstQubit_LCD_fit_test_PCB160.FCStd'
for f in [componentFile,assemblyFile,fitFile]:
 if f.exists():raise RuntimeError('Refusing overwrite: '+str(f))
protected=list(cad.glob('*.FCStd'))+list(library.rglob('*'))+list((root/'enclosure/prints').rglob('*.stl'))+list((root/'firmware').rglob('*'))+[root/'hardware/wiring.md']
hashes={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in protected if f.is_file()}
settings=App.ParamGet('User parameter:BaseApp/Preferences/Document')
oldBackups=settings.GetInt('CountBackupFiles',1);settings.SetInt('CountBackupFiles',0)

def open_file(path):
 return next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==path),None) or App.openDocument(str(path))

original=open_file(library/'GC9A01_META_MCU_candidate.FCStd')
componentDoc=App.newDocument('GC9A01_Drawing_PCB160')
componentDoc.Label='GC9A01 compatible drawing reference - provisional, not measured'
component=componentDoc.addObject('App::Part','CandidateModule')
p=componentDoc.addObject('Spreadsheet::Sheet','DrawingParameters')
values={'PCBThickness':1.6,'PCBWidth':38,'PCBLength':45.5,'LCDOuterWidth':35.6,
 'LCDThickness':1.5,'ActiveDiameter':32.4,'HoleDiameter':2,'HolePitch':23,
 'HoleCenterX':.279993591309,'HoleY':-23.726002144678,
 'PCBFrontSetback':1.999998526721,'SolderPitch':2.54}
for row,(key,value) in enumerate(values.items(),1):
 p.set('A'+str(row),key);p.set('B'+str(row),('=' if value<0 else '')+str(value)+' mm');p.setAlias('B'+str(row),key)
 p.set('C'+str(row),'STEP datum retained, physically unverified' if key in ['HoleCenterX','HoleY','PCBFrontSetback'] else 'User-transcribed compatible drawing; original unavailable, provisional')
p.setColumnWidth('A',180);p.setColumnWidth('C',520)
# Drawing bounds with STEP-derived neck width and center offset, provisional.
# Hole locations are NOT scaled: retain STEP-derived axes pending measurement.
old=original.PCBReference.Shape.cleaned();b=old.BoundBox
lower=min([f for f in old.Faces if type(f.Surface).__name__=='Plane' and f.Area>100],key=lambda f:f.CenterOfMass.z)
for row,key,value in [(14,'NeckWidth',28.5),(15,'OutlineCenterX',.279993591309),(16,'OutlineCenterY',-.281001844678)]:
 p.set('A'+str(row),key);p.set('B'+str(row),('=' if value<0 else '')+str(value)+' mm');p.setAlias('B'+str(row),key);p.set('C'+str(row),'STEP-derived outline approximation, provisional')
roundBoard=componentDoc.addObject('Part::Cylinder','RoundBoardBlank')
roundBoard.setExpression('Radius','DrawingParameters.PCBWidth/2');roundBoard.setExpression('Height','DrawingParameters.PCBThickness')
roundBoard.setExpression('Placement.Base.x','DrawingParameters.OutlineCenterX');roundBoard.setExpression('Placement.Base.y','DrawingParameters.OutlineCenterY')
roundBoard.setExpression('Placement.Base.z','-DrawingParameters.PCBFrontSetback-DrawingParameters.PCBThickness')
neck=componentDoc.addObject('Part::Box','NeckBlank');neck.setExpression('Length','DrawingParameters.NeckWidth');neck.setExpression('Width','DrawingParameters.PCBLength-DrawingParameters.PCBWidth/2');neck.setExpression('Height','DrawingParameters.PCBThickness')
neck.setExpression('Placement.Base.x','DrawingParameters.OutlineCenterX-DrawingParameters.NeckWidth/2')
neck.setExpression('Placement.Base.y','DrawingParameters.OutlineCenterY+DrawingParameters.PCBWidth/2-DrawingParameters.PCBLength')
neck.setExpression('Placement.Base.z','-DrawingParameters.PCBFrontSetback-DrawingParameters.PCBThickness')
slab=componentDoc.addObject('Part::MultiFuse','PCBSlab');slab.Shapes=[roundBoard,neck];slab.Refine=True
holes=[]
for i,sign in enumerate([-1,1]):
 h=componentDoc.addObject('Part::Cylinder','MountingHole'+str(i));h.setExpression('Radius','DrawingParameters.HoleDiameter/2')
 h.setExpression('Height','DrawingParameters.PCBThickness+0.2 mm')
 h.setExpression('Placement.Base.x','DrawingParameters.HoleCenterX'+('+' if sign>0 else '-')+'DrawingParameters.HolePitch/2')
 h.setExpression('Placement.Base.y','DrawingParameters.HoleY')
 h.setExpression('Placement.Base.z','-DrawingParameters.PCBFrontSetback-DrawingParameters.PCBThickness-0.1 mm');holes.append(h)
tool=componentDoc.addObject('Part::MultiFuse','HoleTools');tool.Shapes=holes
board=componentDoc.addObject('Part::Cut','PCBReference');board.Base=slab;board.Tool=tool;board.Refine=True;component.addObject(board)
display=componentDoc.addObject('Part::Cylinder','DisplayBodyReference');component.addObject(display)
display.setExpression('Radius','DrawingParameters.LCDOuterWidth/2');display.setExpression('Height','DrawingParameters.LCDThickness');display.setExpression('Placement.Base.z','-DrawingParameters.LCDThickness')
connector=componentDoc.addObject('Part::Feature','ConnectorReference');component.addObject(connector);connector.Shape=original.ConnectorReference.Shape.cleaned()
connector.Label='Unchanged STEP header geometry - provisional; 11.3 mm NOT assigned'
componentDoc.recompute()
for o in componentDoc.Objects:
 if hasattr(o,'ViewObject'):o.Visibility=False
component.Visibility=True
for o,col in [(board,(.18,.35,.26)),(display,(.12,.13,.14)),(connector,(.65,.55,.28))]:o.Visibility=True;o.ViewObject.ShapeColor=col
componentDoc.recompute();componentDoc.saveAs(str(componentFile))

# Execute only the historical reusable definitions, with new destinations and source.
recipe=(cad/'create_lcd_mechanical_integration.py').read_text()
start=recipe.index('baseValues=');end=recipe.index('\nS=setup(assembly)')
definitions=recipe[start:end]
exec(definitions,globals())
baseValues.update(SourcePCBThickness=1.6,SolderHeightTBD=1.2,BracketRearGapTBD=1.6,
 PilotDiameterTBD=1.2,M2ShankDiameterTBD=1.6,M2HeadDiameterTBD=3.2,M2HeadHeightTBD=1.3)
baseValues.update(PinPitchTBD=2.54,PinDiameterTBD=1,PinRearLengthTBD=2,
 WireWidthTBD=20,WireDepthTBD=8,WireHeightTBD=8,WireBackSetbackTBD=16.8)
# M1.6 is only a candidate, avoiding zero nominal clearance in drawing's 2 mm holes.
candidate=open_file(cad/'MyFirstQubit_iteration03_candidate_LCD.FCStd')
candidate.saveCopy(str(assemblyFile));assembly=App.openDocument(str(assemblyFile))
assembly.Label='Iteration 03 LCD drawing PCB 1.60 - provisional revision'
assembly.LeftCandidateLCD.setLink(component);assembly.RightCandidateLCD.setLink(component)
# Preserve geometry-building logic while redirecting all reports and images.
body=recipe[end:]
body=body.replace("'MyFirstQubit_LCD_Fit_Test'","'MyFirstQubit_LCD_Fit_Test_PCB160'")
body=body.replace("'LCD-mechanical-validation.json'","'LCD-PCB160-validation.json'")
for image in ['LCD-mechanical-inside','LCD-mount-exploded','LCD-mount-section','LCD-fit-test-assembled','LCD-fit-test-print-layout']:
 body=body.replace(image+'.png',image+'-PCB160.png')
# Hash check is performed below with portable paths, extended to original STLs/firmware.
body=body[:body.index('for path,h in hashes.items():')]+"\n"
# Old validation embeds absolute paths; provide empty map, then restore our map.
protectedHashes=hashes;hashes={}
exec(body,globals())
hashes=protectedHashes

def append_envelopes(doc,setup_data,systems_here,centers):
 for side,sys,(cx,cy) in zip(['Left','Right'] if doc==assembly else ['Test'],systems_here,centers):
  # Pins and harness are separate from the STEP header and SMD envelope.
  # No inference is made from the uninspected 11.3 mm drawing annotation.
  pins=[]
  for i in range(7):
   pin=setup_data['cyl'](side+'SolderPinEnvelope'+str(i),'PinDiameterTBD/2','PinRearLengthTBD',
    '('+cx+')+SourceHeaderCenterX+('+str(i-3)+'*PinPitchTBD)',
    '('+cy+')+SourceHeaderCenterY','PCBBack-PinRearLengthTBD',setup_data['reserves'])
   pins.append(pin)
  wire=setup_data['box'](side+'AttachedWireEnvelopeTBD','WireWidthTBD','WireDepthTBD','WireHeightTBD',
   '('+cx+')+SourceHeaderCenterX-WireWidthTBD/2',
   '('+cy+')+SourceHeaderCenterY-WireDepthTBD/2','DisplayFront-WireBackSetbackTBD',setup_data['reserves'])
  wire.Label='PROVISIONAL harness/socket reserve; measure actual wire routing'
  for o in pins+[wire]:o.Visibility=False
  sys['pins']=pins;sys['wire']=wire
 for key,value in [('SourcePCBThickness',1.6),('SolderHeightTBD',1.2),('BracketRearGapTBD',1.6)]:
  setup_data['p'].set('C'+setup_data['aliases'][key][1:],'Compatible drawing provisional' if key!='BracketRearGapTBD' else 'Design: 1.2 mm SMD + 0.4 mm gap; contact lands must be verified')
 for o in doc.Objects:
  if hasattr(o,'Label') and 'M2' in o.Label:o.Label=o.Label.replace('M2','M1.6 PROVISIONAL')
 doc.recompute()

append_envelopes(assembly,S,systems,[('Parameters.LCDLeftX','Parameters.LCDY'),('Parameters.LCDRightX','Parameters.LCDY')])
append_envelopes(fit,F,[single],[('CouponCenterX','CouponCenterY')])
# The native link source changed; label provenance explicitly.
for obj in [assembly.LeftCandidateLCD,assembly.RightCandidateLCD,module]:obj.Label='LCD compatible drawing / STEP hybrid - PCB 1.60 mm provisional'
report=validate()
report['source_status']='Compatible drawing transcribed by user, original unavailable. No numerical Dorhea measurements supplied. STEP retained for hole datums/header; revised dimensions provisional.'
report['protected_sha256']=hashes
report['screw_note']='M1.6 proposal in 2 mm drawing holes, radial nominal clearance 0.2 mm. 1.2 mm pilots and all fastener sizes/type/engagement require physical trial. Legacy M2-named aliases retained for recipe compatibility.'
report['additional_envelope_conflicts']=[]
parts=[front,assembly.RearTrayRounded]+list(assembly.DiscoveryControls.Group)+[assembly.ESP32EnvelopeTBD,assembly.BreadboardEnvelopeTBD]+[sys[k] for sys in systems for k in ['ring','cradle']]
parts=[o for o in parts if hasattr(o,'Shape') and not o.Shape.isNull()]
for sys in systems:
 for envelope in sys['pins']+[sys['wire']]:
  for other in parts:
   volume=envelope.Shape.common(other.Shape).Volume
   if volume>.001:report['additional_envelope_conflicts'].append([envelope.Name,other.Name,volume])
report['new_component_dimensions_mm']={o.Name:[o.Shape.cleaned().BoundBox.XLength,o.Shape.cleaned().BoundBox.YLength,o.Shape.cleaned().BoundBox.ZLength] for o in [board,display,connector]}
report['unchanged_optical_surface_z_mm']=30.8
report['pcb_back_shift_mm']=1.6-.41148
report['cradle_rear_shift_mm']=(1.6-.41148)+(.4)
report['enclosure_thickness_increase_mm']=0
report['annotation_11_3_mm']='Unassigned: original compatible drawing unavailable; not total thickness or pin protrusion.'
report['reopen_errors']=[]
report['parameter_perturbation_errors']=[]
for doc in [assembly,fit]:
 sheet=doc.LCDMountParameters
 cell=sheet.getCellFromAlias('SourcePCBThickness')
 z=doc.getObject('LeftLCDCradle' if doc==assembly else 'TestLCDCradle').Shape.BoundBox.ZMin
 sheet.set(cell,'1.70 mm');doc.recompute()
 dz=doc.getObject('LeftLCDCradle' if doc==assembly else 'TestLCDCradle').Shape.BoundBox.ZMin-z
 if abs(dz+.1)>1e-6:report['parameter_perturbation_errors'].append([doc.Name,dz])
 sheet.set(cell,'='+componentDoc.Name+'#DrawingParameters.PCBThickness');doc.recompute();doc.save()
report['shared_parameter_check']=[]
componentDoc.DrawingParameters.set('B1','1.70 mm');componentDoc.recompute()
for doc in [assembly,fit]:
 doc.recompute()
 if abs(doc.LCDMountParameters.get('SourcePCBThickness').Value-1.7)>1e-6:report['shared_parameter_check'].append(doc.Name)
componentDoc.DrawingParameters.set('B1','1.60 mm');componentDoc.recompute()
for doc in [assembly,fit]:doc.recompute();doc.save()
componentDoc.save()
# Reopen all new native documents from disk and validate every solid shape.
names=[assembly.Name,fit.Name,componentDoc.Name]
for name in names:App.closeDocument(name)
for path in [componentFile,assemblyFile,fitFile]:
 d=open_file(path);d.recompute()
 for o in d.Objects:
  if 'Invalid' in o.State:report['reopen_errors'].append([d.Name,o.Name,str(o.State)])
  if hasattr(o,'Shape') and not o.Shape.isNull() and o.Shape.Solids and not o.Shape.isValid():report['reopen_errors'].append([d.Name,o.Name,'invalid shape'])
for path,h in hashes.items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==h,'Prior file changed: '+path
report['earlier_files_hash_verified']=True
(cad/'LCD-PCB160-validation.json').write_text(json.dumps(report,indent=2)+'\n')
settings.SetInt('CountBackupFiles',oldBackups)
print('REVISION VALIDATION',json.dumps({k:v for k,v in report.items() if k not in ['protected_sha256','clearances']},indent=2))
