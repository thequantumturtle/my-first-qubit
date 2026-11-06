"""FreeCAD MCP: finish shared datums; independently reopen/check PCB160 revision.
No historical CAD or STL is saved. No mesh export is performed.
"""
from pathlib import Path
import json,hashlib
import Part
from pivy import coin
root=Path(globals().get('MFQ_REPO_ROOT',r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit'))
cad=root/'enclosure/freecad'
paths=[root/'hardware/models/gc9a01-meta-mcu/GC9A01_drawing_PCB160_provisional.FCStd',cad/'MyFirstQubit_iteration03_LCD_PCB160.FCStd',cad/'MyFirstQubit_LCD_fit_test_PCB160.FCStd']
def load(path):return next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==path),None) or App.openDocument(str(path))
component,assembly,fit=[load(p) for p in paths]
settings=App.ParamGet('User parameter:BaseApp/Preferences/Document');old=settings.GetInt('CountBackupFiles',1);settings.SetInt('CountBackupFiles',0)
report=json.loads((cad/'LCD-PCB160-validation.json').read_text())
for doc in [assembly,fit]:
 p=doc.LCDMountParameters
 for mount,ref in [('SourcePCBThickness','PCBThickness'),('SourcePCBFrontSetback','PCBFrontSetback'),('SourceHolePitch','HolePitch'),('SourceHoleCenterX','HoleCenterX'),('SourceHoleY','HoleY'),('PinPitchTBD','SolderPitch')]:
  p.set(p.getCellFromAlias(mount),'='+component.Name+'#DrawingParameters.'+ref)
 doc.recompute();doc.save()
# Explicit shape/collision validation of independent fit test (including linked LCD).
printed=[fit.DimensionedFitCoupon,fit.TestLensRetainer,fit.TestLCDCradle]
parts=printed+[fit.TestPolycarbonateLens,fit.TestLCDWorkingReference]
report['fit_assembly_collisions']=[]
report['fit_printable_solids']=[]
for obj in printed:
 report['fit_printable_solids'].append({'name':obj.Name,'valid':obj.Shape.isValid(),'closed':obj.Shape.isClosed(),'solids':len(obj.Shape.Solids),'dimensions_mm':[obj.Shape.BoundBox.XLength,obj.Shape.BoundBox.YLength,obj.Shape.BoundBox.ZLength]})
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  vol=a.Shape.common(b.Shape).Volume
  if vol>.001:report['fit_assembly_collisions'].append([a.Name,b.Name,vol])
report['fit_pin_wire_conflicts']=[]
for envelope in [o for o in fit.Objects if 'SolderPinEnvelope' in o.Name or 'AttachedWireEnvelope' in o.Name]:
 for other in printed+[fit.TestPolycarbonateLens]:
  vol=envelope.Shape.common(other.Shape).Volume
  if vol>.001:report['fit_pin_wire_conflicts'].append([envelope.Name,other.Name,vol])
report['final_stack_z_mm']={key:assembly.LCDMountParameters.get(key).Value for key in ['PanelTop','PanelBottom','LensBottom','DisplayFront','PCBFront','PCBBack','BracketTop','BracketBottom']}
report['shared_parameter_reopen_errors']=[]
for d in [fit,assembly]:App.closeDocument(d.Name)
App.closeDocument(component.Name)
component,assembly,fit=[load(p) for p in paths]
for d in [component,assembly,fit]:
 d.recompute()
 for o in d.Objects:
  if 'Invalid' in o.State:report['shared_parameter_reopen_errors'].append([d.Name,o.Name,str(o.State)])
  if hasattr(o,'Shape') and not o.Shape.isNull() and o.Shape.Solids and not o.Shape.isValid():report['shared_parameter_reopen_errors'].append([d.Name,o.Name,'invalid shape'])
report['final_native_files']=[{'file':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
for relative,digest in report['protected_sha256'].items():assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==digest,relative
report['earlier_files_hash_verified']=True
# Comparative dimensioned axial stack; all positions derive from the native sheet.
z=report['final_stack_z_mm'];scale=22;baseline=920
def y(v):return baseline-v*scale
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="880" viewBox="0 0 1200 880">',
 '<rect width="1200" height="880" fill="#fffdf8"/>',
 '<g font-family="sans-serif" fill="#293b32"><text x="45" y="45" font-size="25">LCD axial stack comparison — millimeters</text>',
 '<text x="45" y="75" font-size="16">Provisional drawing / STEP hybrid. Schematic section; not a manufacturing drawing.</text>']
for x,title,thickness,reargap in [(75,'Historical STEP PCB',.41148,1.2),(640,'Revised compatible-drawing PCB',1.6,1.6)]:
 svg.append(f'<text x="{x}" y="115" font-size="20">{title}</text>')
 layers=[('PC lens 1.5',z['LensBottom'],1.5,'#c5dde0'),('Air gap 2.0',z['DisplayFront'],2,'#eef2ed'),('LCD 1.50',z['DisplayFront']-1.5,1.5,'#444f49'),('PCB '+str(thickness),z['PCBFront']-thickness,thickness,'#698a76'),('Rear reserve '+str(reargap),z['PCBFront']-thickness-reargap,reargap,'#eee4d0'),('Cradle base 2.0',z['PCBFront']-thickness-reargap-2,2,'#a8b7a7')]
 for label,bottom,height,color in layers:
  svg.append(f'<rect x="{x}" y="{y(bottom+height):.3f}" width="210" height="{height*scale:.3f}" fill="{color}" stroke="#33493c"/>')
  svg.append(f'<text x="{x+225}" y="{y(bottom+height/2)+5:.3f}" font-size="15">{label}</text>')
 for label,value in [('Optical front',z['DisplayFront']),('PCB front',z['PCBFront']),('PCB back',z['PCBFront']-thickness),('Cradle rear',z['PCBFront']-thickness-reargap-2)]:
  svg.append(f'<text x="{x}" y="{550+25*["Optical front","PCB front","PCB back","Cradle rear"].index(label)}" font-size="16">{label} Z = {value:.4f}</text>')
svg.extend(['<text x="45" y="690" font-size="18">Unchanged: lens gap 2.0; posts ≈1.5; panel underside/top Z30.3/35.3; enclosure depth.</text>',
 '<text x="45" y="722" font-size="18">Revised: PCB rearward +1.18852; cradle rearward +1.58852; screw engagement 4.38852 → 2.8.</text>',
 '<text x="45" y="754" font-size="17">PCB front setback ≈2.0 remains STEP-derived. No exact Dorhea dimensions verified.</text>',
 '<text x="45" y="786" font-size="17">11.3 mm connector-region annotation UNASSIGNED — original drawing unavailable.</text>',
 '<text x="45" y="824" font-size="18">Adult engineering prototype. No new STL export. Not child-safe or manufacturing-ready.</text></g></svg>'])
(cad/'LCD-PCB160-section-dimensions.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
failureKeys=['invalid','collisions','keepout_conflicts','additional_envelope_conflicts','reopen_errors','parameter_perturbation_errors','shared_parameter_check','fit_assembly_collisions','fit_pin_wire_conflicts','shared_parameter_reopen_errors']
report['validation_passed']=all(not report[k] for k in failureKeys) and all(o['valid'] and o['closed'] and o['solids']==1 for o in report['fit_printable_solids'])
(cad/'LCD-PCB160-validation.json').write_text(json.dumps(report,indent=2)+'\n')
settings.SetInt('CountBackupFiles',old)
App.setActiveDocument(assembly.Name);v=Gui.activeDocument().activeView();v.setCameraType('Orthographic');v.getCameraNode().orientation.setValue(coin.SbRotation(.8804762392171493,-.11591689595929514,.2798481423331213,-.3647051996310009));Gui.updateGui();v.fitAll();Gui.updateGui()
print(json.dumps({k:report[k] for k in failureKeys+['fit_printable_solids','validation_passed']},indent=2))
if not report['validation_passed']:raise RuntimeError('PCB160 validation failed; do not commit/push')
