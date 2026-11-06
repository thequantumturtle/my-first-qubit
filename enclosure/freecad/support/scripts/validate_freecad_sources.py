"""MCP/FreeCAD audit using private mirrored copies; never saves source documents."""
from pathlib import Path
import tempfile,shutil,json,hashlib,zipfile
if 'MFQ_REPO_ROOT' in globals():repo=Path(MFQ_REPO_ROOT).resolve()
elif '__file__' in globals():repo=Path(__file__).resolve().parents[2]
else:raise RuntimeError('Set MFQ_REPO_ROOT before running in FreeCAD')
sources=sorted(list((repo/'hardware/models').rglob('*.FCStd'))+list((repo/'enclosure/freecad').glob('*.FCStd')))
hashes={str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
report={'freecad_version':'.'.join(App.Version()[:3]),'files':[],'errors':[]}
before=set(App.listDocuments())
scratch=Path(tempfile.mkdtemp(prefix='mfq-cad-check-')).resolve()
assert scratch.parent==Path(tempfile.gettempdir()).resolve() and scratch.name.startswith('mfq-cad-check-')
try:
    for p in sources:
        with zipfile.ZipFile(p) as z:
            if z.testzip() is not None:raise RuntimeError('Corrupt CAD archive: '+str(p))
        target=scratch/p.relative_to(repo);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    for p in sources:
        target=scratch/p.relative_to(repo)
        doc=next((d for d in App.listDocuments().values() if Path(d.FileName)==target),None)
        if doc is None:doc=App.openDocument(str(target),True)
        doc.recompute()
        row={'file':str(p.relative_to(repo)).replace('\\','/'),'sha256':hashes[str(p.relative_to(repo))],
             'reopened_from_private_copy':True,'invalid_objects':[], 'external_links':[]}
        for o in doc.Objects:
            if 'Invalid' in o.State:row['invalid_objects'].append([o.Name,o.getStatusString()])
            if o.TypeId=='App::Link':
                linked=o.LinkedObject
                if linked is None or not hasattr(o,'Shape') or o.Shape.isNull():row['invalid_objects'].append([o.Name,'Unresolved/null link'])
                elif linked.Document!=doc:
                    linkedPath=Path(linked.Document.FileName).resolve()
                    portable=linkedPath.is_relative_to(scratch)
                    row['external_links'].append({'name':o.Name,'target_file':str(linkedPath.relative_to(scratch)).replace('\\','/') if portable else str(linkedPath),'resolved_inside_mirror':portable})
                    if not portable:row['invalid_objects'].append([o.Name,'External link did not resolve inside mirrored checkout'])
        if row['invalid_objects']:report['errors'].append(row['file'])
        report['files'].append(row)
        print(row['file'],'errors',row['invalid_objects'],'links',row['external_links'])
finally:
    for name in list(set(App.listDocuments())-before):
        if name in App.listDocuments():App.closeDocument(name)
    # Delete only the verified private directory created above.
    assert scratch.parent==Path(tempfile.gettempdir()).resolve() and scratch.name.startswith('mfq-cad-check-')
    shutil.rmtree(scratch)
for p in sources:assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(repo))]
report['original_bytes_unchanged']=True
out=repo/'enclosure/prints/lcd-fit-test/cad-source-validation.json'
out.write_text(json.dumps(report,indent=2))
if report['errors']:raise RuntimeError('Source reopen/link validation failed: '+repr(report['errors']))
print('PASS:',len(sources),'FreeCAD sources reopened; linked files resolved; originals unchanged')
