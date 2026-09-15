---
name: blender-threejs-environments
description: Coordinate substantial game-environment creation or reconstruction using Blender and Three.js, from reference topology through asset delivery. Use for whole environments or changes spanning layout, art, and runtime; use focused skills directly for isolated edits.
---

# Blender + Three.js environments

Turn references into an aligned, explorable environment with editable sources and verified runtime assets. Preserve the user's style, scope, latest corrections, and authorization. A quality checkpoint means inspect evidence, not ask for permission again.

## Establish the shared contract

Record reference authority, axes/units/origin, route connectivity, boundary polylines, elevations, camera/projection, target devices and visual priorities in the project's existing scene manifest or a compact equivalent. Mark inferred dimensions explicitly. User annotations govern the feature they clarify; generated images are not measured geometry.

Use maps plus sections for stacked spaces. Freeze a comparison camera, but inspect neighboring and walking views to expose one-camera cheats. A coordinate round trip proves transform consistency, not reference fidelity. Assess topology, scale, proportions and appearance separately.

## Route only the work needed

| Work | Skill |
|---|---|
| Map, terrain, architecture placement, collision | [Layout](../../authoring/blender-threejs-layout/SKILL.md) |
| Reference isolation, modeling, lettering, variants, foliage | [Props](../../authoring/blender-threejs-props/SKILL.md) |
| Repeating PBR and anti-repetition sampling | [Materials](../../authoring/blender-threejs-materials/SKILL.md) |
| Contextual wear, deposits, repairs, local markings | [Surface paint](../../authoring/blender-threejs-surface-paint/SKILL.md) |
| Static bounce lighting and runtime lightmaps | [Baked GI](../blender-threejs-baked-gi/SKILL.md) |
| Source/export consistency, loading and ownership | [Asset pipeline](../blender-threejs-asset-pipeline/SKILL.md) |
| CPU/GPU/loading/memory bottlenecks | [Performance](../../validation/threejs-performance/SKILL.md) |
| Reference, traversal, defect isolation, final checks | [Scene QA](../../validation/threejs-scene-qa/SKILL.md) |

## Work in reviewable increments

1. Make a playable clay layout with connected routes, real clearances and aligned ground. Compare landmarks and proportions before detailed assets.
2. Finish one representative assembly and one ground/wall material pair through Blender export and actual Three.js rendering. Resolve coordinate, UV, color-space and silhouette problems before multiplying the kit.
3. Expand modular assets and context-aware painting from that verified example. Preserve hand edits and stable placement identities.
4. Calibrate and pilot lighting before expensive bakes. Publish compatible geometry, maps and probes together.
5. Inspect final encoded assets, saved sources, walking routes, loading failures and controlled performance. Report unmet criteria instead of hiding them through camera or resolution changes.

When scope changes, update shared records and dependent assemblies together. Removed architecture must not reappear through fallback generation. Geometry changes can invalidate paint, collision, lightmaps and measurements; small repairs need an explicit change ledger and affected-receiver analysis.

## Team and source ownership

Use bounded parallel tasks with nonoverlapping file ownership, one integration owner and stable input revisions. Each worker hands over sources, outputs, assumptions, checks and remaining failures. Do not equate many workers with progress.

Start a separate Blender process for the task; create a separate window for interactive work. Never reuse another worker's or the user's open scene. Serialize GPU bakes, captures and benchmarks. CPU-only independent tests can run concurrently.

Use the [handoff worksheet](references/handoffs.md) for multi-worker work. The [evaluation record](references/evaluation.md) documents what this skill set has actually tested.
