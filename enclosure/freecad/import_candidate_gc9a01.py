"""FreeCAD MCP: source-preserving component import and linked I03 study."""
from pathlib import Path
import hashlib,json,math
import Import,Part
from pivy import coin
workspace=Path(r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit')
library=workspace/'hardware/models/gc9a01-meta-mcu'
cad=workspace/'enclosure/freecad'
componentPath=library/'GC9A01_META_MCU_candidate.FCStd'
assemblyPath=cad/'MyFirstQubit_iteration03_candidate_LCD.FCStd'
if componentPath.exists() or assemblyPath.exists():raise RuntimeError('Refusing to overwrite a component or assembly')
protected=list(cad.glob('*.FCStd'))
hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in protected}
step=library/'source/frame_size.step'
component=App.newDocument('GC9A01_META_MCU_Candidate')
Import.insert(str(step),component.Name);component.recompute()
raw=component.getObject('PCB');raw.Label='Original STEP import - unchanged geometry'
board=component.getObject('Part__Feature')
header=component.getObject('P1')
display=component.getObject('Free_Models')
surface=next(f.Surface for f in display.Shape.Faces if type(f.Surface).__name__=='Cylinder')
cx,cy=surface.Center.x,surface.Center.y
top=display.Shape.BoundBox.ZMax
datum=App.Vector(cx,cy,top)
normalized=component.addObject('App::Part','CandidateModule')
normalized.Label='META-MCU GC9A01 candidate - NOT verified Dorhea'
for typ,value in [('SourceURL','https://github.com/META-MCU/gc9a01-tft'),('SourceRevision',(library/'source/REVISION.txt').read_text().strip()),('SourceLicense','EPL-1.0; see source/LICENSE and NOTICE.md'),('MatchStatus','PROVISIONAL: mechanical/electrical equivalence to installed Dorhea boards not established'),('DatumDescription','XY at imported display disk axis; Z=0 at disk front face; +Z toward viewer; header toward -Y')]:
 normalized.addProperty('App::PropertyString',typ,'Provenance');setattr(normalized,typ,value)
for prop,value in [('SourceCenterX',cx),('SourceCenterY',cy),('SourceDisplayTop',top)]:
 normalized.addProperty('App::PropertyLength',prop,'SourceDatum');setattr(normalized,prop,value)
def appearance(o,color,trans=0):
 o.ViewObject.ShapeColor=color;o.ViewObject.Transparency=trans;o.ViewObject.LineColor=(0.18,0.21,0.20)
 m=o.ViewObject.ShapeAppearance[0];m.SpecularColor=(0,0,0);m.Shininess=0.1;o.ViewObject.ShapeAppearance=[m]
shapes=[]
for obj,name,color in [(board,'PCBReference',(0.18,0.37,0.29)),(header,'ConnectorReference',(0.63,0.59,0.43)),(display,'DisplayBodyReference',(0.16,0.19,0.20))]:
 shape=obj.Shape.cleaned();shape.translate(-datum)
 out=component.addObject('Part::Feature',name);normalized.addObject(out);out.Shape=shape
 out.Label=name+' - upstream BRep, not a Dorhea measurement';appearance(out,color);shapes.append(out)
raw.Visibility=False
for obj in raw.OutList:
 if hasattr(obj,'Visibility'):obj.Visibility=False
normalized.Visibility=True
component.recompute()
def bbox(s):
 b=s.cleaned().BoundBox
 return {'min':[b.XMin,b.YMin,b.ZMin],'max':[b.XMax,b.YMax,b.ZMax],'size':[b.XLength,b.YLength,b.ZLength]}
holes=[];pins=[]
for face in board.Shape.Faces:
 s=face.Surface
 if type(s).__name__=='Cylinder':
  if 1<s.Radius<1.1:holes.append({'center_source':[s.Center.x,s.Center.y],'diameter':2*s.Radius})
  if .44<s.Radius<.46:pins.append({'center_source':[s.Center.x,s.Center.y],'diameter':2*s.Radius})
findings={'revision':normalized.SourceRevision,'source_SHA256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (library/'source').iterdir() if p.is_file()},
 'source_display_datum':[cx,cy,top],'model_display_body_diameter':2*surface.Radius,
 'board':bbox(board.Shape),'header':bbox(header.Shape),'display_body':bbox(display.Shape),
 'mounting_holes':holes,'pin_holes':sorted(pins,key=lambda x:x['center_source'][0]),
 'board_circle_center':[14.24999944,25.499999532071],
 'measurement_method':'Cleaned analytic BRep bounds; cached import tessellation understated extents. No scaling or geometry correction.',
 'intrinsic_PCB_connector_overlap_mm3':shapes[0].Shape.common(shapes[1].Shape).Volume,
 'drawing_vs_model_warning':'Drawing width38 and hole dia2 differ from analytic STEP width38.1531627 and holes2.10000088. Imported tessellation gives a smaller cached width38.11935; measurements use cleaned BRep. Drawing/PCB circle datum14.25,25.5 differs from modeled display center13.970006,25.781002. Disk is not an active-area model.',
 'match_status':normalized.MatchStatus}
component.saveAs(str(componentPath))
v=Gui.activeDocument().activeView();v.setCameraType('Orthographic');Gui.Selection.clearSelection()
def shot(view,path,q):
 view.getCameraNode().orientation.setValue(coin.SbRotation(*q));Gui.updateGui();view.fitAll();Gui.updateGui();view.saveImage(str(path),1500,1200,'White')
ax=(0.3647051996310009,0.2798481423331213,0.11591689595929514,0.8804762392171493)
shot(v,library/'candidate-component.png',ax)
source=cad/'MyFirstQubit_enclosure_iteration03.FCStd'
src=next((d for d in App.listDocuments().values() if d.FileName==str(source)),None)
if src is None:src=App.openDocument(str(source))
src.saveCopy(str(assemblyPath))
assembly=App.openDocument(str(assemblyPath));assembly.Label='Iteration 03 - provisional META-MCU LCD integration'
group=assembly.addObject('App::DocumentObjectGroup','CandidateLCDModules')
params=assembly.addObject('Spreadsheet::Sheet','CandidateLCDParameters')
params.set('A1','DisplayFrontZProvisional');params.set('B1','27.3 mm');params.setAlias('B1','DisplayFrontZProvisional')
params.set('C1','Maintains I03 proxy front plane; physical PCB/LCD stack must be measured')
params.set('A2','ExtraSocketDepthTBD');params.set('B2','6 mm');params.setAlias('B2','ExtraSocketDepthTBD')
params.set('C2','Additional wiring/mating reserve beyond modeled rear connector; not measured')
params.setColumnWidth('A',230);params.setColumnWidth('B',100);params.setColumnWidth('C',540)
for name in ['LCDLeftBoardTBD','LCDRightBoardTBD','LeftActiveDisplayProxyTBD','RightActiveDisplayProxyTBD']:
 old=assembly.getObject(name);old.Label='SUPERSEDED proxy: '+old.Label;old.Visibility=False
links=[]
for side,x in [('Left','LCDLeftX'),('Right','LCDRightX')]:
 link=assembly.addObject('App::Link',side+'CandidateLCD');group.addObject(link);link.setLink(normalized)
 link.Label=side+' META-MCU candidate - Dorhea fit UNVERIFIED'
 link.setExpression('Placement.Base.x','Parameters.'+x)
 link.setExpression('Placement.Base.y','Parameters.LCDY')
 link.setExpression('Placement.Base.z','CandidateLCDParameters.DisplayFrontZProvisional')
 link.Visibility=True;links.append(link)
assembly.recompute()
others=[assembly.FrontHousingRounded,assembly.RearTrayRounded]+list(assembly.DiscoveryControls.Group)+list(assembly.ElectronicsPlaceholders.Group)+list(assembly.ProtectedDisplays.Group)
others=[o for o in others if not o.Name.startswith(('LCDLeftBoard','LCDRightBoard','LeftActiveDisplay','RightActiveDisplay'))]
clearances=[];collisions=[]
for link in links:
 for part in shapes:
  shape=part.Shape.copy();shape.transformShape(link.Placement.toMatrix())
  for other in others:
   volume=shape.common(other.Shape).Volume
   dist=shape.distToShape(other.Shape)[0]
   clearances.append({'module':link.Name,'part':part.Name,'other':other.Name,'distance_mm':dist,'overlap_mm3':volume})
   if volume>0.001:collisions.append(clearances[-1])
 # A reserve only, not a claimed mating connector. Do not turn it into a mount.
 b=shapes[1].Shape.cleaned().BoundBox
 reserve=assembly.addObject('Part::Box',link.Name+'MatingReserveTBD');group.addObject(reserve)
 reserve.Label=link.Label.split(' - ')[0]+' extra socket/wire reserve - unverified'
 reserve.Length=b.XLength;reserve.Width=b.YLength
 reserve.setExpression('Height','CandidateLCDParameters.ExtraSocketDepthTBD')
 reserve.setExpression('Placement.Base.x',link.Name+'.Placement.Base.x+'+str(b.XMin)+' mm')
 reserve.setExpression('Placement.Base.y',link.Name+'.Placement.Base.y+'+str(b.YMin)+' mm')
 reserve.setExpression('Placement.Base.z',link.Name+'.Placement.Base.z+'+str(b.ZMin)+' mm-CandidateLCDParameters.ExtraSocketDepthTBD')
 reserve.Visibility=False
assembly.recompute()
reserves=[o for o in group.Group if o.TypeId=='Part::Box']
reserveChecks=[]
for reserve in reserves:
 for other in others:
  vol=reserve.Shape.common(other.Shape).Volume
  if vol>0.001:reserveChecks.append([reserve.Name,other.Name,vol])
results={'source_component':str(componentPath),'display_centers':[[58,158,27.3],[150,158,27.3]],
 'geometry_valid':all(p.Shape.isValid() for p in shapes),'collisions':collisions,
 'clearances':clearances,'extra_socket_reserve_collisions':reserveChecks,
 'source_iteration_hashes':hashes,'cautions':['Source component is NOT verified for Dorhea','Active aperture not modeled','No fabricated mounting holes/bosses added','Solder, wiring and real connector dimensions unverified']}
for link in links:
 print('LINK',link.Name,link.TypeId,link.LinkedObject.Document.FileName,link.Placement)
print('INTERFERENCES',json.dumps(collisions));print('MATING RESERVE INTERFERENCES',reserveChecks)
# Show internal installation from the back, keeping front panel and lens stack.
assembly.RearTrayRounded.Visibility=False
for o in assembly.ElectronicsPlaceholders.Group:o.Visibility=True
for name in ['LCDLeftBoardTBD','LCDRightBoardTBD']:assembly.getObject(name).Visibility=False
for o in assembly.ProtectedDisplays.Group:o.Visibility=True
for name in ['LeftActiveDisplayProxyTBD','RightActiveDisplayProxyTBD']:assembly.getObject(name).Visibility=False
v=Gui.activeDocument().activeView();v.setCameraType('Orthographic');Gui.Selection.clearSelection()
shot(v,cad/'iteration03-candidate-LCD-inside.png',(0.8804762392171493,-0.11591689595929514,0.2798481423331213,-0.3647051996310009))
shot(v,cad/'iteration03-candidate-LCD-rear.png',(1,0,0,0))
# Keep the saved assembly open in the internal inspection view; hide old proxies.
assembly.recompute()
settings=App.ParamGet('User parameter:BaseApp/Preferences/Document');old=settings.GetInt('CountBackupFiles',1);settings.SetInt('CountBackupFiles',0)
try:assembly.save()
finally:settings.SetInt('CountBackupFiles',old)
for f in protected:assert hashlib.sha256(f.read_bytes()).hexdigest()==hashes[str(f)]
(library/'dimensional-findings.json').write_text(json.dumps(findings,indent=2))
(cad/'iteration03-candidate-LCD-clearances.json').write_text(json.dumps(results,indent=2))
print('SAVED',componentPath,assemblyPath)
