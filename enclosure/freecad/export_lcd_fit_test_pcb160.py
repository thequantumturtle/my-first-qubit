"""FreeCAD MCP exporter for the saved PCB160 solids; never saves native sources.

Set MFQ_REPO_ROOT when invoking via MCP. Reuses the historical mesh round-trip
validator with explicit new source/targets, preserving the old export recipe.
"""
from pathlib import Path
import hashlib,json

if 'MFQ_REPO_ROOT' in globals():
    repo=Path(MFQ_REPO_ROOT).resolve()
elif '__file__' in globals():
    repo=Path(__file__).resolve().parents[2]
else:
    raise RuntimeError('Set MFQ_REPO_ROOT before running through FreeCAD MCP')

protected=list((repo/'enclosure/freecad').glob('*.FCStd'))
protected+=list((repo/'enclosure/freecad').glob('*.json'))
protected+=list((repo/'hardware/models').rglob('*'))
protected+=list((repo/'enclosure/prints/lcd-fit-test').glob('*.stl'))
protected+=list((repo/'enclosure/prints/lcd-fit-test').glob('*.json'))
protected+=list((repo/'firmware').rglob('*'))+[repo/'hardware/wiring.md']
protected={p.relative_to(repo).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in protected if p.is_file()}
folder=repo/'enclosure/prints/lcd-fit-test-pcb160'
if any(folder.glob('*.stl')):
    raise RuntimeError('Revised STL files already exist; review before replacing outputs')
recipe=(repo/'enclosure/freecad/export_lcd_fit_test.py').read_text()
recipe=recipe.replace('MyFirstQubit_LCD_fit_test.FCStd','MyFirstQubit_LCD_fit_test_PCB160.FCStd')
recipe=recipe.replace("'enclosure/prints/lcd-fit-test'","'enclosure/prints/lcd-fit-test-pcb160'")
recipe=recipe.replace('lcd-fit-panel.stl','lcd-fit-panel-pcb160.stl')
recipe=recipe.replace('lcd-lens-retainer.stl','lcd-lens-retainer-pcb160.stl')
recipe=recipe.replace('lcd-rear-cradle.stl','lcd-rear-cradle-pcb160.stl')
recipe=recipe.replace("checks['freecad_mesh_is_solid']=loaded.isSolid()", "checks['freecad_mesh_is_solid']=loaded.isSolid()\n    checks['freecad_has_nonmanifolds']=loaded.hasNonManifolds()\n    assert checks['freecad_has_nonmanifolds'] is False")
# A missing self-intersection test is a failed validation, never an implicit pass.
recipe=recipe.replace("checks['self_intersections'] is True","checks['self_intersections'] is not False")
exec(compile(recipe,'export_lcd_fit_test.py [PCB160 source and targets]','exec'),globals())

manifest=json.loads((folder/'validation.json').read_text())
manifest['protected_sha256']=protected
manifest['source_revision']='51333cab9216e78d407e691b62e676a4a1f89a4c'
manifest['checks']['protected_previous_files_unchanged']=all(hashlib.sha256((repo/p).read_bytes()).hexdigest()==h for p,h in protected.items())
assert manifest['checks']['protected_previous_files_unchanged']

# Recheck saved assembly geometry and service clearances without editing it.
assemblyPath=repo/'enclosure/freecad/MyFirstQubit_iteration03_LCD_PCB160.FCStd'
old=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==assemblyPath),None)
if old:
    if old.isTouched():raise RuntimeError('Enclosure assembly has unsaved changes')
    App.closeDocument(old.Name)
assembly=App.openDocument(str(assemblyPath));assembly.recompute()
assert not [o.Name for o in assembly.Objects if 'Invalid' in o.State]
component=assembly.LeftCandidateLCD.LinkedObject.Document
review={'component_reference':'Drawing/STEP hybrid; no exact Dorhea dimensions verified',
 'parameters_mm':{k:doc.LCDMountParameters.get(k).Value for k in ['SourcePCBThickness','SourceHolePitch','PilotDiameterTBD','M2ShankDiameterTBD','M2HeadDiameterTBD','M2HeadHeightTBD','ScrewClearanceTBD','BracketRearGapTBD','SolderHeightTBD','PCBScrewLengthTBD','LensScrewLengthTBD','LensThicknessTBD','LensDiameterTBD','LensGapTargetTBD']},
 'source_hole_diameter_mm':component.DrawingParameters.get('HoleDiameter').Value,
 'physical_dimensions_verified':False,'clearances_mm':[],'collisions':[]}
for side in ['Left','Right']:
    link=assembly.getObject(side+'CandidateLCD')
    obstacles=[assembly.LCDIntegratedFrontHousing,assembly.getObject(side+'LensRetainer'),assembly.getObject(side+'LCDCradle'),assembly.getObject(side+'PolycarbonateLensTBD')]
    for sourceName in ['PCBReference','DisplayBodyReference','ConnectorReference']:
        shape=component.getObject(sourceName).Shape.copy();shape.transformShape(link.Placement.toMatrix())
        for obstacle in obstacles:
            volume=shape.common(obstacle.Shape).Volume
            review['clearances_mm'].append([side,sourceName,obstacle.Name,shape.distToShape(obstacle.Shape)[0],volume])
            if volume>.001:review['collisions'].append([side,sourceName,obstacle.Name,volume])
p=doc.LCDMountParameters
mm=lambda key:p.get(key).Value
review['pcb_screw_engagement_mm']=mm('BracketBottom')+mm('PCBScrewLengthTBD')-mm('PCBFront')
review['lens_screw_engagement_mm']=mm('FlangeBottom')+mm('LensScrewLengthTBD')-mm('PanelBottom')
review['driver_access_note']='Remove cradle and LCD before lens-ring screws; straight PCB screw approach checked in the preserved CAD validation.'
review['prior_mechanical_report']='enclosure/freecad/LCD-PCB160-validation.json'
review['prior_report_passed']=json.loads((repo/review['prior_mechanical_report']).read_text())['validation_passed']
assert not review['collisions'] and review['prior_report_passed']
assert all(hashlib.sha256((repo/p).read_bytes()).hexdigest()==h for p,h in protected.items())
manifest['mechanical_recheck']=review
(folder/'validation.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PCB160 export and mechanical recheck passed; all protected bytes unchanged.')
