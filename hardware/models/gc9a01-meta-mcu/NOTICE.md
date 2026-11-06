# META-MCU GC9A01 candidate: provenance and license

Upstream repository: https://github.com/META-MCU/gc9a01-tft

Revision inspected/downloaded: `8f2157d11d97182927e2d3d9475cf28df620feb1`.
Retrieved October 21, 2026. Attribution: META-MCU/gc9a01-tft contributors.
The STEP header uses the generic author string `Author`; no more specific CAD
authorship is asserted here. The imported connector carries the source name
`pcb_connector_800-10-007-66-001101`.

The repository declares **Eclipse Public License 1.0 (EPL-1.0)** in its root
LICENSE, with no separate CAD license found in the inspected file tree. Preserve
the complete [upstream license](source/LICENSE), all source notices, and the
unchanged STEP/drawing when redistributing this candidate reference material.
The upstream license permits distribution subject to its terms. This records
the stated repository license; it does not establish third-party ownership or
manufacturer endorsement, nor grant rights to physical hardware patents.
Do not apply this notice as a blanket license for the enclosure repository.

Unchanged reference files:

- `source/frame_size.step`: upstream `assembly diagram/frame_size.step`.
- `source/frame_size.jpg`: upstream `assembly diagram/frame_size.jpg`.
- `source/upstream-readme.md`: upstream `readme.md`, filename changed locally.
- `source/LICENSE`: full unmodified upstream license.
- `source/REVISION.txt`: local record of the requested upstream revision.

Pinned download base:
`https://raw.githubusercontent.com/META-MCU/gc9a01-tft/8f2157d11d97182927e2d3d9475cf28df620feb1/`
Original paths containing spaces are URL-encoded for download. Source checksums
are recorded in `dimensional-findings.json`.

Local contribution by the My First Qubit project: FreeCAD import, source-datum
normalization, provenance fields, display colors, dimensional inspection and
engineering documentation. The original import tree is retained in the component
document; normalized parts are translated copies of the three source BReps with
cached tessellation removed, not reshaped or scaled. The conversion recipe is
`../../../enclosure/freecad/import_candidate_gc9a01.py` from this directory.
The candidate component and its upstream-derived geometry retain EPL-1.0 terms;
the original STEP and conversion recipe remain available alongside the documents
for source access. No original notice has been removed. No files were committed
or published during this task.
