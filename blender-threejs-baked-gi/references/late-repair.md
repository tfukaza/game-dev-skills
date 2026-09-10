# Artifact diagnosis and bounded late repair

Hold camera, preset, geometry and sampling constant when isolating a defect.
Compare: actual GI/materials; GI off with actual materials; neutral receiver
material with GI; uncompressed versus encoded lighting; direct shadows off.
These are diagnostic fixtures, never final appearance evidence for substitute
assets. Keep their provenance explicit.

| Observation | Investigate before changing appearance |
| --- | --- |
| Colored blocks in dim neutral surfaces | Codec reconstruction and matched filtering |
| Isolated warm bright samples in linear/uncompressed data | Monte Carlo outliers and local statistics |
| Black base/jamb bands | Internal/coplanar faces, gaps, wrong receiver side and atlas bleed |
| Regular diagonal ground striations | Shadow acne, projection texel size, bias and normal bias |
| Globally wrong brightness | EXR transfer, pass units and doubled light contributions |

Do not repair transport or geometry errors with broad contrast/exposure changes.
Shadow bias should suppress self-acne while bounding contact displacement; a
number copied from another scene is not sufficient. Fit stable projections to
the intended scene bounds and inspect both light directions.

Keep immutable raw passes plus source/atlas/rig/sample hashes. Resume only after
every checkpoint dependency and completed-pass hash matches. A temporary joined
bake carrier can reduce overhead, but first compare original-corner UVs, world
positions, normals, coverage and a small AO/transport bake. Restore original
objects and material links before source publication.

A selective face rebake is valid only when the repair's influence is bounded.
Changing an occluder or bounce surface can affect remote texels; unchanged UVs
alone do not prove unaffected transport. If remote influence cannot be excluded,
rebake the affected transport globally. For a justified local receiver repair,
preserve the atlas/corner attributes, audit repaired geometry, bake exactly its
coverage, merge into a new copy of raw passes, and prove nonselected raw texels
remain unchanged. Rebuild guides from the corrected donor, then refilter/pad and
encode. Do not reuse old chart IDs merely because the array dimensions match.

Revisions must change with repaired geometry, lighting or encoding. Restamp
matching receivers, regenerate dependent probes, and verify the reloaded editable
source. Publish the coherent set only after actual-map runtime review. A CPU/GPU
bake-device change also merits a parity/timing pilot; one tested Metal pilot was
slower and did not establish radiance parity, so it was not promoted.
