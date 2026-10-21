# Native CAD and engineering records

Use FreeCAD 1.0.2 or a compatible later version. Open native documents directly;
do not run a construction recipe merely to view them. Keep `hardware/models/`
in the same checkout so external LCD links resolve. Source reopen/link checks
are recorded in [cad-source-validation.json](../prints/lcd-fit-test/cad-source-validation.json).

| Native document | Purpose |
| --- | --- |
| [Iteration 01](MyFirstQubit_enclosure_iteration01.FCStd) | Initial housing and all nine physical controls |
| [Iteration 02](MyFirstQubit_enclosure_iteration02.FCStd) | Organized gate group and stronger Measure hierarchy |
| [Iteration 03](MyFirstQubit_enclosure_iteration03.FCStd) | Calm Montessori/Waldorf-inspired appearance, rounded surfaces and preliminary lenses |
| [Candidate LCD placement](MyFirstQubit_iteration03_candidate_LCD.FCStd) | Historical provisional imported-module comparison |
| [LCD mechanical integration](MyFirstQubit_iteration03_LCD_mechanical_integration.FCStd) | Working LCD reference, rear mounts, cradle and captured lens |
| [Independent LCD fit test](MyFirstQubit_LCD_fit_test.FCStd) | Three small printable test parts; no full enclosure export |
| [Battery packaging proposal](MyFirstQubit_enclosure_v04_battery_proposal.FCStd) | Separate V0.4 NiMH space study, not yet merged with the latest LCD mounts |

Read [LCD-mechanical-review.md](LCD-mechanical-review.md) for the current working
model confirmation register, the 2 mm gap study, remaining measurements and
known limitations. Earlier reviews are historical snapshots; their earlier
"no exports" or "unverified match" statements describe those stages.

## Print preparation and validation

- [Manufacturing files/settings](../prints/lcd-fit-test/README.md)
- [Illustrated assembly/checklist](../../docs/lcd-fit-test-assembly.md)
- [Dimensioned coupon drawing](LCD-fit-test-dimensions.svg)
- `export_lcd_fit_test.py`: selective export and round-trip mesh validation.
- `validate_freecad_sources.py`: reopen private copies and resolve external links.
- `validate_release.py`: run with ordinary Python to check mesh topology,
  dimensions/volumes/hashes, local documentation links, SVGs and license presence.

For the first two scripts, run inside FreeCAD using this pattern, setting the
checkout directory to your own path:

```python
from pathlib import Path
MFQ_REPO_ROOT = r"C:\path\to\my-first-qubit"
script = Path(MFQ_REPO_ROOT) / "enclosure/freecad/export_lcd_fit_test.py"
exec(compile(script.read_text(), str(script), "exec"))
```

The older construction scripts preserve the original modeling recipes, including
their original local path settings. Inspect/edit their paths and choose new
output names before reuse; several intentionally refuse overwriting outputs.
They are provenance, not a requirement for loading the saved parametric files.
Historical JSON reports may contain the original local source paths; new print
reports use repository-relative file identifiers. Backups and superseded raw
inspection screenshots stay local through `.gitignore`.

The fit-test exporter does not save or alter CAD. Mesh dimensions are in mm by
convention; the STL format itself is unitless. Digital geometry validation is
separate from physical fit, material, impact, retention and child-safety testing.
# Latest LCD dimensional study

The [provisional 1.60 mm PCB revision](LCD-PCB160-review.md) adds separate
component, enclosure and fit-test documents, with an updated section and
validation report. Previous sources and the three historical STLs are unchanged.
Do not use the old print package for the revised stack without review.
