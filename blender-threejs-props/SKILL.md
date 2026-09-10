---
name: blender-threejs-props
description: Author reusable Blender and Three.js game props from references, including modular models, image-generated surface lettering, coherent variants, foliage, support contacts and consistent detail levels. Use for prop creation or placement quality rather than whole-level layout.
---

# Blender + Three.js props

Build coherent physical objects from the requested reference, scale, construction and style. Establish silhouette and proportions before spending detail on grain or lettering. For placement-only edits, use grounding/contact guidance without regenerating artwork, variants or the asset library.

## Select the module

- [Reference isolation and modular modeling](references/reference-modeling.md): isolate one asset, resolve alternate views, split complex assemblies and define units/pivots.
- [Surface graphics](references/surface-graphics.md): game-appropriate image-generated artwork, exact wording, surface registration and source preservation.
- [Variant families](references/variant-families.md): coordinated construction, graphics and material variation without stretched duplicates.
- [Foliage and attachment](references/foliage-attachment.md): structured organic variation, supported detail and grounded placement.
- [Prop contracts and tools](references/prop-contracts.md): stable parameter generation and exported bounds/channel/detail-level checks.
- [Evaluation](references/evaluation.md): tested helper cases and remaining visual checks.

Prefer image-generated lettering artwork appropriate to the game's setting instead of generic operating-system fonts. Verify actual spelling and reuse canonical artwork across views. A generated wordmark is an image, not a complete installable font. Use the available image-generation skill/tool for bitmap authoring rather than duplicating its tool instructions here.

Painted text belongs in the actual surface UV artwork or a conforming decal. Floating glyph meshes or detached cards are not substitutes. Model physical placards and genuinely raised lettering when the intended construction calls for them.

Reused objects should be coherent variant families, not one textured mesh stretched to arbitrary dimensions. Keep stable geometry/graphics/material identities through load order and LOD changes, and preserve resource sharing.

## Ground, export and inspect

Record units, axes, pivot, nominal dimensions, support/attachment anchors and collision purpose. Verify transformed base/support vertices against the actual receiver. A Y0 pivot or minimum bounding-box Y does not prove contact after rotation, scale, leaning or slope placement. Do not add an unintended flat pad to hide a transform error.

Inspect close-up, in context and through detail transitions. Verify silhouettes, cloth folds, roots, supports, exact lettering and material response on the actual export. Bounds and metadata tests cannot prove these visual properties.

Use [asset pipeline](../blender-threejs-asset-pipeline/SKILL.md) for GLB preservation, [layout](../blender-threejs-layout/SKILL.md) for terrain/collision, [materials](../blender-threejs-materials/SKILL.md) for PBR response, [surface paint](../blender-threejs-surface-paint/SKILL.md) for graphic projection/baking and [performance](../threejs-performance/SKILL.md) for measured resource tradeoffs.
