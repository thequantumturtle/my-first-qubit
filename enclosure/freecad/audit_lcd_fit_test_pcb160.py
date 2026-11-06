"""Independent binary-STL topology/bounds audit, using only Python stdlib.
Run: py enclosure/freecad/audit_lcd_fit_test_pcb160.py
Does not modify any files. Self-intersection result comes from FreeCAD's
round-trip test, tied to each actual STL by SHA256.
"""
from pathlib import Path
from collections import Counter,defaultdict
import ast,hashlib,json,math,re,struct
from urllib.parse import unquote,urlsplit
import xml.etree.ElementTree as ET

repo=Path(__file__).resolve().parents[2]
folder=repo/'enclosure/prints/lcd-fit-test-pcb160'
manifest=json.loads((folder/'validation.json').read_text())
expected={'lcd-fit-panel-pcb160.stl','lcd-lens-retainer-pcb160.stl','lcd-rear-cradle-pcb160.stl'}
assert {p.name for p in folder.glob('*.stl')}==expected
assert {p['file'] for p in manifest['parts']}==expected
assert manifest['checks']['source_reopened'] and manifest['checks']['source_bytes_unchanged']
assert not manifest['mechanical_recheck']['collisions']
assert hashlib.sha256((repo/manifest['source']).read_bytes()).hexdigest()==manifest['source_sha256']
for filename,digest in manifest['protected_sha256'].items():
    assert hashlib.sha256((repo/filename).read_bytes()).hexdigest()==digest,filename

for part in manifest['parts']:
    data=(folder/part['file']).read_bytes()
    assert hashlib.sha256(data).hexdigest()==part['sha256']
    count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*count
    vertices={};points=[];faces=[]
    for i in range(count):
        values=struct.unpack_from('<12fH',data,84+i*50)
        face=[]
        for j in [3,6,9]:
            point=tuple(values[j:j+3]);assert all(math.isfinite(v) for v in point)
            if point not in vertices:vertices[point]=len(points);points.append(point)
            face.append(vertices[point])
        faces.append(tuple(face))
    assert len(faces)==len({tuple(sorted(f)) for f in faces}),'Duplicate surfaces'
    edge_counts=Counter();directions=Counter();owners=defaultdict(list);links=defaultdict(list);volume=0
    for i,(a,b,c) in enumerate(faces):
        assert len({a,b,c})==3
        pa,pb,pc=[points[j] for j in [a,b,c]]
        ab=[pb[j]-pa[j] for j in range(3)];ac=[pc[j]-pa[j] for j in range(3)]
        cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        assert sum(v*v for v in cross)>1e-20,'Degenerate triangle'
        volume+=(pa[0]*(pb[1]*pc[2]-pb[2]*pc[1])+pa[1]*(pb[2]*pc[0]-pb[0]*pc[2])+pa[2]*(pb[0]*pc[1]-pb[1]*pc[0]))/6
        for u,v in [(a,b),(b,c),(c,a)]:
            edge=tuple(sorted((u,v)));edge_counts[edge]+=1;directions[edge]+=1 if u<v else -1;owners[edge].append(i)
        links[a].append((b,c));links[b].append((c,a));links[c].append((a,b))
    assert all(n==2 for n in edge_counts.values()),'Nonmanifold/boundary edge'
    assert not any(directions.values()),'Inconsistent winding'
    # Each closed-surface vertex must have exactly one cycle as its link.
    for edges in links.values():
        adjacency=defaultdict(set)
        for u,v in edges:adjacency[u].add(v);adjacency[v].add(u)
        assert all(len(v)==2 for v in adjacency.values()),'Nonmanifold vertex'
        todo=[next(iter(adjacency))];seen=set()
        while todo:
            u=todo.pop()
            if u in seen:continue
            seen.add(u);todo.extend(adjacency[u]-seen)
        assert len(seen)==len(adjacency),'Pinched/nonmanifold vertex'
    adjacency=defaultdict(set)
    for fs in owners.values():
        a,b=fs;adjacency[a].add(b);adjacency[b].add(a)
    todo=[0];seen=set()
    while todo:
        f=todo.pop()
        if f in seen:continue
        seen.add(f);todo.extend(adjacency[f]-seen)
    assert len(seen)==len(faces),'Disconnected shell'
    assert volume>0
    minimum=[min(p[j] for p in points) for j in range(3)]
    dimensions=[max(p[j] for p in points)-minimum[j] for j in range(3)]
    assert max(abs(a-b) for a,b in zip(dimensions,part['cad_dimensions_mm']))<.001
    # Tessellation can inset curved XY extrema by <0.001 mm; bed plane is exact.
    assert abs(minimum[2])<1e-5 and max(abs(v) for v in minimum[:2])<.001,'Orientation/origin not on bed'
    assert abs(volume-part['cad_volume_mm3'])/part['cad_volume_mm3']<.0003
    assert part['checks']['self_intersections'] is False
    assert part['checks']['connected_components']==1 and part['checks']['freecad_mesh_is_solid']
    print(f"PASS {part['file']}: {count} triangles, manifold edges/vertices, one oriented closed shell; "+' x '.join(f'{v:.4f}' for v in dimensions)+' mm')

for path in [repo/'AGENTS.md',repo/'README.md']+list((repo/'enclosure').rglob('*.md'))+list((repo/'docs').rglob('*.md'))+list((repo/'hardware').rglob('*.md')):
    if path.name=='upstream-readme.md':continue
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
        target=target.strip().strip('<>');url=urlsplit(target)
        if not url.scheme and url.path:assert (path.parent/unquote(url.path)).resolve().exists(),(path,target)
for path in (repo/'enclosure/freecad').glob('*.svg'):ET.parse(path)
for filename in ['export_lcd_fit_test_pcb160.py','audit_lcd_fit_test_pcb160.py']:
    ast.parse((repo/'enclosure/freecad'/filename).read_text())
print('PASS source/history/firmware/wiring hashes, three-file scope, documentation links, SVG and recipe syntax. No physical/slicer qualification implied.')
