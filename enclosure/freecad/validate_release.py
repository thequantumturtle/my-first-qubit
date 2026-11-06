"""Standard-library audit of the print package and local documentation links.
Run: py enclosure/freecad/validate_release.py
FreeCAD-specific mesh self-intersection/source-reopen checks are in validation.json.
"""
from pathlib import Path
from collections import Counter,defaultdict
from urllib.parse import unquote,urlsplit
import hashlib,json,math,re,struct,sys,xml.etree.ElementTree as ET

repo=Path(__file__).resolve().parents[2]
prints=repo/'enclosure/prints/lcd-fit-test'
manifest=json.loads((prints/'validation.json').read_text())
errors=[];summaries=[]
expected={'lcd-fit-panel.stl','lcd-lens-retainer.stl','lcd-rear-cradle.stl'}
if {p.name for p in prints.glob('*.stl')}!=expected:errors.append('Unexpected/missing print STL files')
if {p['file'] for p in manifest['parts']}!=expected:errors.append('Unexpected manifest entries')
for part in manifest['parts']:
    path=prints/part['file'];data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=part['sha256']:errors.append('Hash mismatch: '+path.name)
    count=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+count*50:raise RuntimeError('Expected binary STL: '+path.name)
    vertices={};points=[];faces=[]
    for i in range(count):
        values=struct.unpack_from('<12fH',data,84+i*50)
        face=[]
        for j in [3,6,9]:
            point=tuple(values[j:j+3])
            if not all(math.isfinite(v) for v in point):errors.append('Nonfinite coordinates: '+path.name)
            if point not in vertices:vertices[point]=len(points);points.append(point)
            face.append(vertices[point])
        faces.append(tuple(face))
    edgeCounts=Counter();directions=Counter();owners=defaultdict(list);volume=0;zero=0
    for i,f in enumerate(faces):
        a,b,c=[points[j] for j in f]
        ab=[b[j]-a[j] for j in range(3)];ac=[c[j]-a[j] for j in range(3)]
        cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        if sum(v*v for v in cross)<1e-20:zero+=1
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for u,v in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
            e=tuple(sorted((u,v)));edgeCounts[e]+=1;directions[e]+=1 if u<v else -1;owners[e].append(i)
    adjacency=defaultdict(set)
    for fs in owners.values():
        for f in fs:adjacency[f].update(fs)
    unseen=set(range(count));components=0
    while unseen:
        components+=1;stack=[unseen.pop()]
        while stack:
            for f in adjacency[stack.pop()]:
                if f in unseen:unseen.remove(f);stack.append(f)
    duplicates=count-len({tuple(sorted(f)) for f in faces})
    if zero or duplicates or components!=1 or any(v!=2 for v in edgeCounts.values()) or any(directions.values()) or volume<=0:
        errors.append('Mesh topology/orientation failed: '+path.name)
    minimum=[min(v[i] for v in points) for i in range(3)]
    dims=[max(v[i] for v in points)-minimum[i] for i in range(3)]
    if max(abs(a-b) for a,b in zip(dims,part['cad_dimensions_mm']))>.05 or abs(minimum[2])>1e-5:
        errors.append('Mesh bounds differ from CAD/bed: '+path.name)
    if abs(volume-part['cad_volume_mm3'])/part['cad_volume_mm3']>.005:errors.append('Volume failed: '+path.name)
    summaries.append(f'{path.name}: {count} triangles, 1 watertight component, bounds '+', '.join(f'{d:.4f}' for d in dims)+' mm')

# Validate local links in tracked/relevant Markdown, not external availability.
for path in [repo/'README.md',repo/'AGENTS.md']+list((repo/'enclosure').rglob('*.md'))+list((repo/'docs').rglob('*.md'))+list((repo/'hardware').rglob('*.md')):
    if path.name=='upstream-readme.md':continue # Original third-party relative links require its full upstream tree.
    body=path.read_text(encoding='utf-8-sig')
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',body):
        target=target.strip().strip('<>');url=urlsplit(target)
        if url.scheme or target.startswith('#') or not url.path:continue
        local=(path.parent/unquote(url.path)).resolve()
        if not local.exists():errors.append(str(path.relative_to(repo))+': broken link '+target)
for path in (repo/'enclosure/freecad').glob('*.svg'):ET.parse(path)
if hashlib.sha256((repo/manifest['source']).read_bytes()).hexdigest()!=manifest['source_sha256']:
    errors.append('Source CAD changed since mesh export')
cadReport=json.loads((prints/'cad-source-validation.json').read_text())
if cadReport['errors'] or not cadReport['original_bytes_unchanged']:errors.append('FreeCAD reopen checks failed')
for row in cadReport['files']:
    if hashlib.sha256((repo/row['file']).read_bytes()).hexdigest()!=row['sha256']:errors.append('CAD changed since reopen validation: '+row['file'])
    if row['invalid_objects'] or any(not link['resolved_inside_mirror'] for link in row['external_links']):errors.append('Invalid native CAD or unresolved reference: '+row['file'])
licensePath=repo/'hardware/models/gc9a01-meta-mcu/source/LICENSE'
if 'Eclipse Public License - v 1.0' not in licensePath.read_text():errors.append('Missing upstream license')
for s in summaries:print(s)
if errors:
    for e in errors:print('FAIL:',e)
    sys.exit(1)
print('PASS: independent STL topology/bounds/volume, CAD hash, local documentation links, SVG syntax and license presence')
