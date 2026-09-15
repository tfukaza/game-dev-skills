---
name: threejs-scene-qa
description: Verify Three.js game scenes through reference comparisons, traversal, render-defect isolation, asset failures, and resource lifecycle checks. Use for scene acceptance or visible 3D defects; performance optimization belongs to threejs-performance and ordinary interface review belongs to UI/UX skills.
---

# Three.js scene QA

Inspect the actual delivered scene. Source correctness, export success, mathematical consistency and visual acceptance are separate evidence.

## Choose the check

- For layout, proportions and traversal: [reference and walking checks](references/reference-traversal.md).
- For noise, bands, seams, floating decals or wrong lighting: [artifact diagnosis](references/artifact-diagnosis.md).
- For staged loading, cancellation and remount: [lifecycle checks](references/lifecycle.md).
- For adapter-based captures and probes: [tools](references/tools.md).
- For tested scope and independent cases: [evaluation record](references/evaluation.md).

Lock camera/projection, lighting, viewport, drawing-buffer size and asset revisions for comparisons. Inspect overview, neighboring and walking-height views, plus grazing angles where joins, decals and normal errors appear. A fixed camera alone can hide incorrect topology.

Use independent review for substantial scene work: give the reviewer the user's references, intended behavior and current artifacts, without prescribing the expected verdict. Correct the diagnosed layer, then repeat the affected checks. Do not accumulate unrelated tests after the relevant concern is resolved.

For frame-time and memory claims use [performance](../threejs-performance/SKILL.md), which owns measurement tools. For GLB/UV preservation use [asset pipeline](../../pipeline/blender-threejs-asset-pipeline/SKILL.md). Never equate mocked lifecycle tests, a screenshot or a low draw count with complete acceptance.

Record what passed, failed or remains untested, with source/runtime revision, conditions and reproducible evidence. Preserve failed comparisons and report unmet targets honestly.
