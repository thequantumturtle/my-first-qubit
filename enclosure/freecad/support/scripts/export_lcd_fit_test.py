"""Run inside FreeCAD via exec(compile(...)) with MFQ_REPO_ROOT set in globals.
Exports only three explicitly named fit-test solids; never saves the CAD source.
"""
from pathlib import Path
import math,json,hashlib
from collections import Counter,defaultdict
import Part,Mesh,MeshPart

if 'MFQ_REPO_ROOT' in globals():
    repo=Path(MFQ_REPO_ROOT).resolve()
elif '__file__' in globals():
    repo=Path(__file__).resolve().parents[2]
else:
    raise RuntimeError('Set MFQ_REPO_ROOT to your checkout path before executing this script in FreeCAD MCP')
source=repo/'enclosure/freecad/MyFirstQubit_LCD_fit_test.FCStd'
output=repo/'enclosure/prints/lcd-fit-test'
output.mkdir(parents=True,exist_ok=True)
before=hashlib.sha256(source.read_bytes()).hexdigest()
# Reopen the file from disk, so the export cannot silently use unsaved edits.
old=next((d for d in App.listDocuments().values() if Path(d.FileName)==source),None)
if old is not None:
    if old.isTouched():
        raise RuntimeError('Fit-test document has unsaved changes; save or review them before export')
    App.closeDocument(old.Name)
doc=App.openDocument(str(source));doc.recompute()
errors=[o.Name for o in doc.Objects if 'Invalid' in o.State]
if errors:raise RuntimeError('Source recompute errors: '+repr(errors))
report={'units':'mm (STL has no encoded unit; import in slicer as millimeters)',
 'freecad_version':'.'.join(App.Version()[:3]),
 'source':'enclosure/freecad/MyFirstQubit_LCD_fit_test.FCStd','source_sha256':before,
 'linear_deflection_mm':0.02,'angular_deflection_degrees':5,
 'checks':{'source_reopened':True,'source_recompute_errors':errors},'parts':[]}

def dimensions(box):return [box.XLength,box.YLength,box.ZLength]
def topology_checks(mesh):
    points,faces=mesh.Topology
    counts=Counter();directions=Counter();seen=set();duplicates=0;degenerate=0
    adjacent=defaultdict(set);owners=defaultdict(list)
    for i,f in enumerate(faces):
        key=tuple(sorted(f))
        if key in seen:duplicates+=1
        seen.add(key)
        a,b,c=[points[j] for j in f]
        if (b-a).cross(c-a).Length<1e-10:degenerate+=1
        for u,v in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
            edge=tuple(sorted((u,v)));counts[edge]+=1;directions[edge]+=1 if u<v else -1;owners[edge].append(i)
    for fs in owners.values():
        for f in fs:adjacent[f].update(fs)
    unseen=set(range(len(faces)));components=0
    while unseen:
        components+=1;todo=[unseen.pop()]
        while todo:
            for f in adjacent[todo.pop()]:
                if f in unseen:unseen.remove(f);todo.append(f)
    return {'facets':len(faces),'points':len(points),
      'boundary_edges':sum(n==1 for n in counts.values()),
      'nonmanifold_edges':sum(n!=2 for n in counts.values()),
      'inconsistent_winding_edges':sum(n!=0 for n in directions.values()),
      'duplicate_facets':duplicates,'degenerate_facets':degenerate,'connected_components':components}

for name,filename,rotate in [
 ('DimensionedFitCoupon','lcd-fit-panel.stl',True),
 ('TestLensRetainer','lcd-lens-retainer.stl',False),
 ('TestLCDCradle','lcd-rear-cradle.stl',False)]:
    obj=doc.getObject(name);shape=obj.Shape.cleaned()
    if not shape.isValid() or not shape.isClosed() or len(shape.Solids)!=1:
        raise RuntimeError('Invalid, open, or multiple CAD solids: '+name)
    if rotate:shape.rotate(App.Vector(0,0,0),App.Vector(1,0,0),180)
    box=shape.cleaned().BoundBox
    shape.translate(App.Vector(-box.XMin,-box.YMin,-box.ZMin))
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.02,AngularDeflection=math.radians(5),Relative=False)
    path=output/filename;mesh.write(str(path))
    # Round-trip file verification, not only the in-memory tessellation.
    loaded=Mesh.Mesh(str(path));checks=topology_checks(loaded)
    checks['freecad_mesh_is_solid']=loaded.isSolid()
    checks['self_intersections']=loaded.hasSelfIntersections() if hasattr(loaded,'hasSelfIntersections') else 'not available'
    expected=dimensions(shape.cleaned().BoundBox);actual=dimensions(loaded.BoundBox)
    error=max(abs(a-b) for a,b in zip(expected,actual))
    volume_error=abs(abs(loaded.Volume)-shape.Volume)/shape.Volume
    row={'file':filename,'source_object':name,'orientation':'front face on bed' if rotate else 'flat rear/flange base on bed',
      'cad_dimensions_mm':expected,'stl_dimensions_mm':actual,
      'max_dimension_error_mm':error,'cad_volume_mm3':shape.Volume,
      'mesh_volume_mm3':abs(loaded.Volume),'relative_volume_error':volume_error,
      'minimum_z_mm':loaded.BoundBox.ZMin,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checks':checks}
    report['parts'].append(row)
    if any(checks[k] for k in ['boundary_edges','nonmanifold_edges','inconsistent_winding_edges','duplicate_facets','degenerate_facets']) or checks['connected_components']!=1 or not checks['freecad_mesh_is_solid'] or checks['self_intersections'] is True or error>.05 or volume_error>.005:
        raise RuntimeError('Mesh check failed: '+json.dumps(row))
assert hashlib.sha256(source.read_bytes()).hexdigest()==before,'Source file changed during export'
report['checks']['source_bytes_unchanged']=True
(output/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
