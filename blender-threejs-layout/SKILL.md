---
name: blender-threejs-layout
description: Build or revise playable Blender and Three.js environment layouts from maps, screenshots, annotations or a design brief. Use for topology, scale, terrain, architecture placement, connections and collision clearance.
---

Turn references into a coherent, playable spatial contract before investing in surface detail. Preserve the user's latest composition and route decisions; an older image or generated fallback must not silently restore removed structures.

## Establish the spatial contract

- Record units, up/forward axes, map orientation, calibration assumptions and the authority of each reference. A map may establish connectivity while a perspective image establishes grouping and appearance. A reversible image transform is not evidence of surveyed dimensions or visual fidelity.
- Separate route topology, dimensional ratios, camera/framing and appearance. Fixing a ratio generally requires changing its components; uniformly scaling everything preserves the ratio.
- Put footprints, levels, openings, landmark transforms and shared boundaries in one editable definition. Geometry, collision, attachments, grounding and surface metadata consume that definition. Work in assembly-local coordinates when an entire structure may move or rotate.

Read [spatial contracts](references/spatial-contracts.md) for terrain, joints and late layout changes. Use [height_contact.py](scripts/height_contact.py) for a monotone profile, shared sample stations or contact checks against explicit upward triangles; its input/output contract and limits are in that reference.

## Build and inspect the relevant geometry

Use a clay overview, a nearby oblique view and relevant eye-height route views to check silhouette, proportions and connections. These are internal evidence checks, not extra permission requests. Continue the authorized work after resolving their findings.

An underpass needs physical clearance beneath its actual deck or arch. Do not place an uninterrupted base plate over a lower floor, close cropped exits with decorative boundaries, or add another tunnel to compensate for incorrectly placed architecture. On sloped terrain, share heights, derivatives and boundary samples with sidewalks, curbs and foundations. Declare nonplanar triangulation explicitly in both Blender and runtime.

Compose architectural variation through footprint, massing, recess depth, roofline and bounded component differences. Random colors on identical boxes do not establish the requested architecture. For new bitmap facade artwork, reference boards, signs or texture motifs, prefer the available image-generation tool; retain simple procedural masks where they are a better fit. Artwork cannot substitute for required openings or structural depth.

Run the actual player/controller against procedural and exported collision when traversal is part of the task. Recheck thresholds, sloped junctions, transformed cover and overhead clearance after relevant edits. A visible floor without collision support is incomplete; bounding boxes alone do not demonstrate passage.

## Compose with the package

- Use [props](../blender-threejs-props/SKILL.md) for asset variants, pivots and physical contact.
- Use [asset pipeline](../blender-threejs-asset-pipeline/SKILL.md) when exporting or comparing Blender/runtime artifacts.
- Use [scene QA](../threejs-scene-qa/SKILL.md) for broader visual and interaction verification; use [performance](../threejs-performance/SKILL.md) for measured runtime cost.

See [evaluation](references/evaluation.md) for helper tests and behavioral checks. Report what the evidence establishes and which dimensions or references remain assumptions.
