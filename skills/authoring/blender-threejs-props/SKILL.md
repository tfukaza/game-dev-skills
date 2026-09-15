---
name: blender-threejs-props
description: Author and review reusable Blender game props from references, including proportions, surface graphics, coherent variants, foliage, placement contacts and Three.js asset contracts. Routes mechanical assemblies, coaster cars and UV authoring to their focused skills.
---

# Blender game props

Establish the object's identity, silhouette, proportions and construction before surface detail. Keep the user's asset scope, style and polygon budget. Placement-only edits need contact checks, not a new reference-generation or asset-library workflow.

## Choose the relevant workflow

- [Shared source-to-model workflow](references/reference-modeling.md): direct original-image inspection, source inventory, simple mockups, generated angles and scope-aware acceptance. Read for reference-driven creation or substantial polish.
- [Mechanical props and vehicles](../blender-mechanical-props/SKILL.md): assembly architecture, connected shells, pivots, hardware, motion and human interaction.
- [Roller coaster cars](../roller-coaster-cars/SKILL.md): target-specific module/bogie topology, rail contact and seating/restraint construction.
- [Blender UV textures](../blender-uv-textures/SKILL.md): actual mesh unwrapping, exported layout, generated artwork and mapped-model inspection.
- [Stylized figurines](references/stylized-figurines.md): cohesive low-poly bodies, clean clothing regions, rig duplication and animation contact checks.
- [Surface graphics](references/surface-graphics.md), [variants](references/variant-families.md), [foliage/attachment](references/foliage-attachment.md), and [prop contracts](references/prop-contracts.md): use only the relevant modules. Existing helper scripts and contract tests remain in this package.

Use image generation for original bitmap artwork when appropriate; follow its available tool/skill. Preserve canonical graphics across views. Painted lettering belongs on a surface UV or conforming decal; detached glyphs are not a substitute. Physical signs and raised lettering need their intended construction.

Every component author and reviewer must personally inspect relevant original images. A summary, generated reference or previous signoff is not visual evidence. Substantial reference-driven creation/polish requires a separate critical review sub-agent following [evaluation](references/evaluation.md), comparing all major components against originals even when the latest repair is narrow. Lead with material mismatches or missing evidence; a local repair cannot imply overall fidelity.

## Place and deliver

Record units, axes, pivot, nominal dimensions, attachment anchors and collision purpose. Check transformed support samples against the actual receiver, not merely a pivot or bounding-box minimum. Do not hide contact errors with an unintended pad. Preserve component/resource identity through variants and LODs.

Inspect close-up, in context and through relevant detail transitions. Use [asset pipeline](../../pipeline/blender-threejs-asset-pipeline/SKILL.md) for GLB preservation, [layout](../blender-threejs-layout/SKILL.md) for terrain/collision, [materials](../blender-threejs-materials/SKILL.md) for PBR response, [surface paint](../blender-threejs-surface-paint/SKILL.md) for projection/wear and [performance](../../validation/threejs-performance/SKILL.md) for measured resource tradeoffs.
