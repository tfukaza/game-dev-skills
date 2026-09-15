# Prop evaluation

## Required independent visual review

Before reporting substantial reference-driven asset creation or polish complete, delegate a strict visual review to a separate sub-agent. This is an asset-quality gate, not a requirement for trivial placement-only changes. If delegation or the necessary rendered evidence is unavailable, state that the review is incomplete rather than claiming a passed review.

Provide the reviewer with the user's intended style and geometry budget, original authoritative photographs, generated reference views, and actual model renders or clearly readable Blender viewport captures. Include several angles: front, side and three-quarter views that expose depth, plus rear/underside or close-up views wherever the construction needs them. Provide both clay/checker and textured evidence where geometry and mapping could mask one another. Include the actual UV layout, texture and island manifest for fitted artwork. Identify the model revision under review so fixes cannot be confused with older captures.

Ask the reviewer to compare the model against **both** original photographs and generated references, with the photographs taking precedence when they conflict.

The reviewer must personally inspect the relevant originals and build a compact correspondence table for **all major components of the asset**, including during a focused cleanup review. This is a check of the asset being reviewed, not an invitation to audit unrelated props or the whole project. For each component record:

| Original feature and specific photo/region evidence | Modeled counterpart and rendered view | Status and required action |
| --- | --- | --- |
| Visible count/grouping, silhouette, enclosing extent or functional relationship | What is actually represented, including omissions | Matched, material mismatch, unresolved/not evaluated, or intentional deviation justified by the brief |

Use concrete observations, not an inventory paraphrase or a blanket "source viewed" claim. For repeated hardware preserve visible minima and distinguish separate parts from hubs, treads and brackets. Uncertain hidden totals are not grounds for accepting fewer parts than the originals visibly show. Inspect relationships across components: isolated panels may be individually attractive while failing to surround or support the intended assembly. See the [source inventory guidance](reference-modeling.md) for count and occlusion handling.

Before treating a generated reference sheet as usable evidence, inspect its actual angles and cross-view consistency: common component axes, correct feature counts after occlusion, transverse overlap in exact side views, plausible visibility of vertical panels from above, and corresponding silhouette/attachment landmarks. Reject mislabeled or contradictory panels even if their individual render quality is high. Refer to [reference-modeling checks](reference-modeling.md) for repairing a drifting sheet through separately generated views.

The author must also self-review generated references for physical/mechanical plausibility before accepting them or starting detailed modeling. Compare functional interfaces and support relationships with original references and, where needed, a simple contact/clearance cross-section or schematic. The independent model reviewer should receive that interpretation and any unresolved uncertainty; generated hardware must not silently become the source of truth.

Have the reviewer actively look for:

- Proportions, silhouette, thickness, volume and spacing from multiple angles.
- Directional shape trends from the source or brief: where curvature tightens, taper increases, or slope changes. Smooth tangency and absence of mesh gaps do not establish that these trends are correct. Compare equal-scale profiles and relevant numeric trends before accepting a footprint-driven reshape.
- Plausible construction and connections, recognizable mechanical hardware, and unsupported or missing parts. For assemblies, compare rigid/articulated module architecture and support ownership with applicable domain/user context as well as visible evidence; do not assume hidden structure is photographically inferable. Use the [mechanical workflow](../../blender-mechanical-props/references/assembly-modeling.md).
- For reference architecture, compare actual side elevations for roof pitch and wall-top relationships, then inspect foundation contacts from a low oblique view. A polished front facade does not establish that the roof geometry or base supports match. For planted props, judge the full crown height/width ratio independently of contact and clearance tests.
- Detail allocation appropriate to the intended viewing distance and polygon budget.
- Sensible sharp versus rounded edges, continuous curved forms and shading that does not hide blocky silhouettes.
- Overall appearance, material response and fidelity to the intended design.
- UV stretching, seam/gutter leakage, orientation, mirrored or misplaced artwork and consistency between the exported layout and applied texture.

Require findings to name the affected component, severity, specific view/evidence and the visible mismatch or consequence. Separate definite defects from uncertain hidden construction and subjective style preferences. The reviewer must identify missing views that prevent a useful assessment; it must not infer visual quality from scripts, object counts, metadata or triangle totals. Generated reference images are authoring aids, not proof of a completed model.

Lead the verdict with outstanding material mismatches and unresolved major components. A successful local repair may be reported, but must not become an unqualified PASS or overall fidelity claim while the correspondence table still contains major omissions or contradictions. Broad fidelity remains failed or incomplete as appropriate. Do not demote a known missing structural group or visible count mismatch to a minor style limitation merely because it was not edited in this pass. A requested low-poly style permits suitable detail reduction, not silently omitting defining components.

Carry known deviations prominently into the final report and any handoff, together with their source evidence and required next step. Mark genuinely unexamined components unresolved instead of silently excluding them. Intentional deviations must be supported by the user's brief or established design direction; calling an omission "simplified" is not by itself a fidelity justification.

Fix material issues before completion, render fresh evidence and request re-review of affected views and any interfaces changed by the fix. Keep unresolved minor tradeoffs explicit. The final review should identify the revision examined and whether any material visual findings remain; silence or a successful numeric check is not signoff.

## Executed reference rejection check

An independent review inspected an actual generated four-panel reference sheet for a complex seated vehicle. It rejected the sheet despite its polished appearance and front/side/rear/top labels: the top panel contained three seats while the front and rear contained four; the top body's forward axis and the seat forward axes disagreed; upright seat backs appeared frontally in the supposed overhead view; and the supposed side view exposed a diagonal row of transverse seats that should overlap in exact side projection. These were directly visible image defects, not findings inferred from prompts or metadata.

This demonstrates a useful rejection check on one failed reference sheet. It does not establish that regenerated references, a modeled asset, UV mapping or the complete visual pipeline passed review.

## Executed helper checks

On 2026-09-10, from this skill folder:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Result: **7 tests passed**, no skips. [test_prop_contract.py](../scripts/test_prop_contract.py) generates compact export-fact fixtures in memory and exercises both CLI modes through cleaned-up temporary files. Python's standard library is sufficient.

Observed deterministic variant:

```json
{"seed":"yard","id":"a","widthRange":[0.96,1.04],"artChoices":["A","B","C"],"result":{"width":1.0185829346273672,"art":"A"}}
```

Insertion, ordering and adding a new variation channel preserve the existing `width` and `art` values. Changing the seed changes the result. A 200-ID fixture remains within its width range and artwork choices.

The export fixture passes with LOD0 **12 triangles**, LOD1 **8 triangles**, both dimensions `[2,1,1]` metres and bounds `[[-1,0,-0.5],[1,1,0.5]]`. It deliberately uses different topology, demonstrating a contract comparison rather than raw-vertex equality. Synthetic normals and blank UVs test array contracts only; this fixture is not an attractive prop or a surface-quality test.

Assertions detect a 0.1 m translated pivot, shrinking geometry hidden by an unused extreme vertex, missing UV/tangent channels, changed semantic IDs or artwork identity, bad indices and unsupported units. CLI exit codes 0, 1 and 2 distinguish pass, valid failed contract and malformed input.

## Behavioral scenarios ready for forward testing

These scenarios are specified but **not yet executed** as independent agent evaluations.

| Scenario | Expected behavior and observable pass condition |
| --- | --- |
| Make six related cargo props that share a style but look constructed differently. | Establish scale and pivots; vary silhouette/construction and graphics within functional limits. Use generated bitmap artwork when useful. Six recolors of one unchanged cube fail this scenario. |
| Label a curved drum with an illustrated panel and exact serial text. | Prefer image generation for new pictorial artwork, add exact lettering deterministically if needed, place the print on the curved surface through the intended UVs. Floating glyph meshes or detached transparent label cards fail unless explicitly part of the reference. |
| Place a leaning crate and a stacked soft bag on a slope. | Transform actual support samples, distinguish intended contact from sag/clearance, and check the receiving geometry. A pivot-only placement or hidden pad fails; closeups and numeric contact evidence agree. |
| Reorder 100 placements and add LODs to an existing library. | Stable IDs preserve variants and runtime bindings through insertion and compaction. Pivots, bounds, artwork identity and required channels survive export; inspect visible LOD transitions. |

The reusable principles are stable identity, meaningful variation, physical contact and cross-LOD intent. The choice of a bottom-centred pivot, exact variation ranges, triangle counts and texture sizes belongs to each asset/project.

## Packaging check

Python syntax and all relative links pass. The official validator returned **Skill is valid!** (exit 0):

```sh
python3 /path/to/skill-creator/scripts/quick_validate.py /path/to/blender-threejs-props
```

These absolute paths record this run; the shipped helper has no dependency on them or on PyYAML. Automated contract checks do not replace final appearance or contact inspection.

## Verify the saved artifact after diagnostics

Reload or append the final saved asset and inspect its mapped appearance before delivery. A beauty render taken before wireframe/checker diagnostics does not prove the saved file is correct. Replacing or clearing Blender material slots can reset per-polygon material indices; preserve and restore both slot bindings and polygon indices, then confirm the saved artifact uses the intended materials. Light/dark cutout tests must show the actual textured material, not an opaque diagnostic override.
