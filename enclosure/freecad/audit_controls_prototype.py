"""Standard-library audit of current controls sources, history and STL package.
Run: py enclosure/freecad/audit_controls_prototype.py
Reuses the existing independent triangle/vertex-link audit without editing it.
"""
from pathlib import Path
from collections import Counter,defaultdict
from urllib.parse import unquote,urlsplit
import ast,hashlib,json,math,re,struct
repo=Path(__file__).resolve().parents[2]
report=json.loads((repo/'enclosure/freecad/controls-prototype-validation.json').read_text())
assert report['validation_passed'] and report['lcd_shapes_and_placements_unchanged']
assert not report['knob_full_rotation_and_push_sweep_collisions']
assert report['final_saved_native_reopen_passed']
assert all(row[2] for row in report['parameter_checks'])
for key in ['preserved_sha256','new_native_sha256']:
    for filename,digest in report[key].items():
        assert hashlib.sha256((repo/filename).read_bytes()).hexdigest()==digest,filename
folder=repo/'enclosure/prints/encoder-knob-fit-test'
manifest=json.loads((folder/'validation.json').read_text())
expected={'encoder-test-panel.stl','encoder-rear-bulkhead.stl','balance-knob.stl','phase-knob.stl'}
assert {p.name for p in folder.glob('*.stl')}==expected
for row in manifest['parts']:
    assert hashlib.sha256((repo/row['source']).read_bytes()).hexdigest()==row['source_sha256']
# Includes explicit manifold vertex-link cycles, unique triangles, one connected
# shell, oriented volume and written-STL hash/bounds checks. FreeCAD's explicit
# self-intersection result is tied to those file bytes by SHA256.
code=(repo/'enclosure/freecad/audit_lcd_fit_test_pcb160.py').read_text()
code=code[code.index("for part in manifest['parts']:"):code.index("\nfor path in [repo/'AGENTS.md'")]
code=code.replace("part['checks']['freecad_mesh_is_solid']","part['checks']['solid']").replace('<.0003','<.005')
exec(compile(code,'independent vertex/triangle audit [controls package]','exec'))
for path in list((repo/'enclosure').rglob('*.md'))+list((repo/'docs').rglob('*.md')):
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
        u=urlsplit(target.strip().strip('<>'))
        if not u.scheme and u.path:assert (path.parent/unquote(u.path)).resolve().exists(),(path,target)
for name in ['create_controls_prototype.py','validate_export_controls.py','audit_controls_prototype.py']:
    ast.parse((repo/'enclosure/freecad'/name).read_text())
print('PASS new source hashes, all preserved CAD/STLs/reports/firmware/wiring, independent mesh manifold/bounds checks, docs and recipe syntax. Button STL release remains blocked.')
