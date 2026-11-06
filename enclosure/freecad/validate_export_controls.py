"""FreeCAD MCP: validate new controls and export encoder calibration solids only.
No button mesh release until the actual switch stack/travel is measured.
"""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,math
import Part,Mesh,MeshPart
root=Path(globals().get('MFQ_REPO_ROOT',r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit'))
cad=root/'enclosure/freecad';out=root/'enclosure/prints/encoder-knob-fit-test'
report=json.loads((cad/'controls-prototype-validation.json').read_text())
def load(path):return next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==path),None) or App.openDocument(str(path))
docs=[load(root/row['file']) for row in report['documents']];assembly,fixture,gate,measure=docs
settings=App.ParamGet('User parameter:BaseApp/Preferences/Document');backup=settings.GetInt('CountBackupFiles',1);settings.SetInt('CountBackupFiles',0)
report['parameter_checks']=[]
for d in docs:
 p=d.ControlDimensions;isEncoder=hasattr(d,'BalanceRemovableKnob')
 name='KnobDiameter' if isEncoder else 'TravelStopTBD';obj=d.BalanceRemovableKnob if isEncoder else d.getObject('GateRearGuideAndStop' if d==gate else 'MeasureRearGuideAndStop')
 cell=p.getCellFromAlias(name);saved=p.getContents(cell);before=obj.Shape.Volume;value=p.get(name).Value
 p.set(cell,str(value+.2)+' mm');d.recompute();passed=abs(obj.Shape.Volume-before)>1e-6
 p.set(cell,saved);d.recompute();report['parameter_checks'].append([d.Name,name,passed])
 for prefix in ['X','Y','Z','H','Gate','Measure','Reset','Colors']:
  if not d.getObject(prefix+'CaptiveCap'):continue
  color=(.66,.42,.32) if prefix=='Measure' else (.67,.58,.35) if prefix in ['Reset','Colors'] else (.48,.60,.52)
  for suffix in ['CapBlank','CapRounded','CaptiveFlange','Pusher','CaptiveCap']:
   part=d.getObject(prefix+suffix);material=part.ViewObject.ShapeAppearance[0];material.DiffuseColor=color;material.SpecularColor=(0,0,0);material.Shininess=.1;part.ViewObject.ShapeAppearance=[material]*len(part.Shape.Faces)
 d.recompute()
 # Finish consistent matte appearance after all booleans have recomputed.
 for o in d.PrintedControlParts.Group:
  color=tuple(o.ViewObject.ShapeColor)[:3];material=o.ViewObject.ShapeAppearance[0];material.DiffuseColor=color;material.SpecularColor=(0,0,0);material.Shininess=.1;o.ViewObject.ShapeAppearance=[material]*len(o.Shape.Faces)
 d.save()
settings.SetInt('CountBackupFiles',backup)
report['reference_collisions']=[];report['existing_electronics_collisions']=[];report['motion_collisions']=[]
for d in docs:
 printed=list(d.PrintedControlParts.Group);refs=list(d.ControlHardwareReferences.Group)
 for part in printed:
  for ref in refs:
   if not ref.Shape.isNull():
    vol=part.Shape.common(ref.Shape).Volume
    if vol>.001:report['reference_collisions'].append([d.Name,part.Name,ref.Name,vol])
 if d in [gate,measure]:
  prefix='Gate' if d==gate else 'Measure';cap=d.getObject(prefix+'CaptiveCap');moving=cap.Shape.copy();moving.translate(App.Vector(0,0,-d.ControlDimensions.get('TravelStopTBD').Value))
  for part in printed:
   if part==cap:continue
   volume=moving.common(part.Shape).Volume
   if volume>.001:report['motion_collisions'].append([d.Name,part.Name,volume])
 for o in d.Objects:
  if 'Invalid' in o.State:report['reopen_errors'].append([d.Name,o.Name,str(o.State)])

old=load(cad/'MyFirstQubit_iteration03_LCD_PCB160.FCStd')
names=['LeftCandidateLCD','RightCandidateLCD','LeftPolycarbonateLensTBD','RightPolycarbonateLensTBD','LeftLensRetainer','RightLensRetainer','LeftLCDCradle','RightLCDCradle','RearTrayRounded','ESP32EnvelopeTBD','BreadboardEnvelopeTBD','WiringReserveTBD']
report['lcd_shapes_and_placements_unchanged']=True
for name in names[:8]:
 a,b=assembly.getObject(name),old.getObject(name)
 if abs(a.Shape.Volume-b.Shape.Volume)>1e-5 or (a.Placement.Base-b.Placement.Base).Length>1e-6:report['lcd_shapes_and_placements_unchanged']=False
for new in list(assembly.PrintedControlParts.Group)+list(assembly.ControlHardwareReferences.Group)+list(assembly.ControlClearanceEnvelopes.Group):
 if new.Name=='ControlsFrontHousing':continue
 for name in names:
  existing=assembly.getObject(name)
  volume=new.Shape.common(existing.Shape).Volume
  if volume>.001:report['existing_electronics_collisions'].append([new.Name,name,volume])
report['layout_clearances_mm']=[]
controls=[('Balance',58,108,20),('Phase',150,108,20),('X',32,65,14),('Y',80,65,14),('Z',128,65,14),('H',176,65,14),('Measure',104,28,18),('Reset',40,28,11),('Colors',168,28,11)]
for i,(a,x,y,r) in enumerate(controls):
 for b,xx,yy,rr in controls[i+1:]:report['layout_clearances_mm'].append([a,b,math.hypot(x-xx,y-yy),math.hypot(x-xx,y-yy)-r-rr])
report['minimum_front_control_gap_mm']=min(row[3] for row in report['layout_clearances_mm'])
report['knob_to_display_center_pitch_mm']=50
report['knob_to_lens_plan_gap_mm']=50-20-19
report['knob_face_gap_mm']=1.3;report['worst_nominal_gap_after_encoder_push_mm']=.5
report['button_nominal_actuation_mm']=.6-.2
report['button_actuation_validated']=False
report['knob_full_rotation_and_push_sweep_collisions']=[]
for side,x in [('Balance',58),('Phase',150)]:
 sweep=Part.makeCylinder(20,14,App.Vector(x,108,36.6-.8))
 for other in list(assembly.PrintedControlParts.Group)+[assembly.LeftCandidateLCD,assembly.RightCandidateLCD,assembly.LeftPolycarbonateLensTBD,assembly.RightPolycarbonateLensTBD]:
  if other.Name==side+'RemovableKnob':continue
  volume=sweep.common(other.Shape).Volume
  if volume>.001:report['knob_full_rotation_and_push_sweep_collisions'].append([side,other.Name,volume])
report['rear_breadboard_to_button_deck_gap_mm']=assembly.ControlDimensions.get('DeckBottom').Value-assembly.BreadboardEnvelopeTBD.Shape.BoundBox.ZMax
report['fillet_editing_note']='Native Part::Fillet Edges radii editable directly. KnobRounding/CapRounding sheet entries are recipe defaults; changing them alone does not alter existing native fillets.'
report['validation_passed']=not any(report[k] for k in ['invalid','collisions','reopen_errors','reference_collisions','existing_electronics_collisions','motion_collisions','knob_full_rotation_and_push_sweep_collisions']) and all(row[2] for row in report['parameter_checks']) and report['lcd_shapes_and_placements_unchanged']
for relative,digest in report['preserved_sha256'].items():assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==digest,relative
if not report['validation_passed']:
 (cad/'controls-prototype-validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['reference_collisions','existing_electronics_collisions','motion_collisions','parameter_checks']},indent=2));raise RuntimeError('Controls validation failed; no exports or commit')

# Reopen finalized new files; no historical source is saved.
for d in docs:App.closeDocument(d.Name)
docs=[App.openDocument(str(root/row['file'])) for row in report['documents']];assembly,fixture,gate,measure=docs
for d in docs:
 d.recompute();assert not [o.Name for o in d.Objects if 'Invalid' in o.State]
report['final_saved_native_reopen_passed']=True
out.mkdir(parents=True,exist_ok=True)
if list(out.glob('*.stl')):raise RuntimeError('Encoder calibration STL outputs already exist; refusing overwrite')
recipe=(cad/'export_lcd_fit_test.py').read_text();exec(recipe[recipe.index('def dimensions('):recipe.index('\nfor name,filename,rotate in')],globals())
manifest={'units':'mm; STL unitless, import at 100% as millimeters','purpose':'Adult encoder mechanical calibration, not retention/strength qualification','linear_deflection_mm':.02,'angular_deflection_degrees':5,'parts':[]}
for d,name,filename,flip in [(fixture,'EncoderTestPanel','encoder-test-panel.stl',True),(fixture,'BalanceRearBulkhead','encoder-rear-bulkhead.stl',True),(fixture,'BalanceRemovableKnob','balance-knob.stl',False),(assembly,'PhaseRemovableKnob','phase-knob.stl',False)]:
 obj=d.getObject(name);shape=obj.Shape.cleaned();assert shape.isValid() and shape.isClosed() and len(shape.Solids)==1
 if flip:shape.rotate(App.Vector(),App.Vector(1,0,0),180)
 b=shape.optimalBoundingBox(False,False);shape.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
 mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.02,AngularDeflection=math.radians(5),Relative=False)
 path=out/filename;mesh.write(str(path));loaded=Mesh.Mesh(str(path));checks=topology_checks(loaded)
 checks.update(solid=loaded.isSolid(),self_intersections=loaded.hasSelfIntersections(),nonmanifolds=loaded.hasNonManifolds())
 assert not any(checks[k] for k in ['boundary_edges','nonmanifold_edges','inconsistent_winding_edges','duplicate_facets','degenerate_facets','self_intersections','nonmanifolds']) and checks['solid'] and checks['connected_components']==1
 expected=dimensions(shape.optimalBoundingBox(False,False));actual=dimensions(loaded.BoundBox)
 assert max(abs(a-b) for a,b in zip(expected,actual))<.03 and abs(loaded.BoundBox.ZMin)<1e-5
 assert abs(abs(loaded.Volume)-shape.Volume)/shape.Volume<.005
 manifest['parts'].append({'file':filename,'source':Path(d.FileName).relative_to(root).as_posix(),'source_object':name,'source_sha256':hashlib.sha256(Path(d.FileName).read_bytes()).hexdigest(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dimensions_mm':actual,'cad_dimensions_mm':expected,'cad_volume_mm3':shape.Volume,'mesh_volume_mm3':abs(loaded.Volume),'checks':checks})
report['new_native_sha256']={row['file']:hashlib.sha256((root/row['file']).read_bytes()).hexdigest() for row in report['documents']}
(cad/'controls-prototype-validation.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'validation.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'validation_passed':report['validation_passed'],'front_gap_min_mm':report['minimum_front_control_gap_mm'],'encoder_exports':manifest},indent=2))
