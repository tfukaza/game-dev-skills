# Prop evaluation

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
