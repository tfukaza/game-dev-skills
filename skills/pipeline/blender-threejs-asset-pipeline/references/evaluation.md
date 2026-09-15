# Asset-pipeline evaluation

## Executed helper checks

On 2026-09-10, from this skill folder:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Result: **9 tests passed**, no skips. [test_glb_audit.py](../scripts/test_glb_audit.py) builds tiny GLBs in memory; CLI fixtures live only in cleaned-up temporary directories. No Blender, network, NumPy or decoder is needed.

Observed fixtures:

| Fixture | Result |
| --- | --- |
| Two-triangle square, four source vertices versus six split/reordered candidate vertices, interleaved candidate buffers | Original POSITION/NORMAL/TANGENT/UV0/UV1 corners preserved; declared UV2 addition passes. Undeclared addition fails. |
| UV2 covering one square with a shared diagonal | 2 triangles, area sum 1, zero overlaps; passes. |
| Two triangles deliberately sharing the same half-square chart | 1 positive-area overlap, area 0.5; fails. |
| Changed UV0, changed tangent handedness, reversed winding, material roughness or node transform | Each strict comparison fails. |
| Changed lighting revision in node extras | Fails normally; passes only with the explicitly named allowed extra key. Unrelated transform change still fails. |
| Changed embedded image bytes or document extras | Fails. The synthetic image payload is opaque data, not an image-decoding test. |
| Animation, skin, sparse accessor, compression, external buffer, morph target or repeated mesh instance | Explicit unsupported-input error. |
| Out-of-range accessor, misalignment, cyclic hierarchy, bad scene roots, NaN or combined matrix/TRS | Explicit malformed-input error. |

The CLI is exercised end to end: exit 0 with a passing declared UV addition, exit 1 for a valid failed comparison, exit 2 with structured stderr for a malformed GLB. No test silently skips missing fixture data.

## Behavioral scenarios ready for forward testing

These are evaluation designs, **not claims of independent agent runs**.

| Scenario | Expected behavior and observable pass condition |
| --- | --- |
| Add a unique lighting UV channel to an approved static export whose exporter splits vertices. | Compare original triangle-corner attributes and metadata, audit the new channel globally, stage a candidate and record hashes. A vertex-count comparison alone fails. |
| A donor is Draco-compressed and uses instancing. | State the helper boundary and obtain a decoded, explicitly expanded audit copy with a documented correspondence, or use a suitable trusted auditor. Never report this helper passed unsupported input. |
| Fix a small coplanar wall overlap after lighting is baked. | Record an intentional changed-face delta; preserve unaffected UVs/attributes, mark newly exposed receivers and route selective lighting work to the GI skill. Do not call changed geometry “unchanged” by ignoring failed comparisons. |
| Leave the scene while model decode and dependent textures are loading, then re-enter. | Late allocated objects are cleaned up, shared resources survive their owners, hooks restore, and working objects are not downgraded by a later fallback. Verify repeated teardown/reopen with actual resource behavior. |
| Publish a new model while texture/probe manifests still reference an old revision. | Stage and validate a matching set, exercise the delivered URLs, retain a usable fallback on mismatch and report delivered content hashes. A nearby successful candidate does not prove publication. |

General invariants are explicit artifact contracts, faithful corner attributes, supported-input honesty, coherent revisions and resource ownership. Specific UV channel numbers, texture codecs, atlas sizes and project mesh names are not universal defaults. Compression/performance tradeoffs belong to [performance](../../../validation/threejs-performance/SKILL.md); transport and filtering belong to [baked GI](../../blender-threejs-baked-gi/SKILL.md).

## Packaging check

Python syntax and all relative links pass. The official validator returned **Skill is valid!** (exit 0):

```sh
python3 /path/to/skill-creator/scripts/quick_validate.py /path/to/blender-threejs-asset-pipeline
```

These absolute paths document this validation run. The portable stdlib helper does not depend on the validation environment or PyYAML.
