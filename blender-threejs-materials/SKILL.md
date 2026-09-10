---
name: blender-threejs-materials
description: Author or revise Blender-to-Three.js PBR surface materials, including physical texture scale and stochastic tiling with coherent color, roughness and normals. Use for material appearance and repetition; broad environmental wear belongs to blender-threejs-surface-paint.
---
# Blender and Three.js surface materials

Establish the material's construction and physical scale before adding texture detail or resolution. Separate repeating surface detail, unique paint and illumination. Preserve the project's UV channels, tangents and material ownership; do not impose this package's example conventions on an existing asset.

1. Inspect the reference and current material in a neutral view. Identify the repeat scale, directional structure, roughness, relief and broad color variation. Keep contrast restrained when stronger grain would compete with the reference's large forms.
2. Build one representative surface before propagation. Use color as sRGB and normals/ORM/masks as linear data. Changes to surface state should affect the appropriate PBR properties coherently. Keep sunlight, shadows and ambient fill out of base color.
3. If repetition is visible, read [stochastic sampling](references/stochastic.md). Vary regions in a stable coordinate field and share transforms/weights across PBR channels. Continuous floors should share a field; directional courses need constrained rotation and scale. Unique paint stays independent.
4. Inspect the actual exported material at close and oblique views, in both relevant lighting conditions and texture tiers. Confirm that uncovered sides/roofs also receive the material. Read [integration and diagnosis](references/integration.md) for UV, shader lifecycle and noise pitfalls.
5. Retain editable source maps, generators and material graphs. Verify a saved-source reload and the delivered file, not just the open Blender session. Report measured limitations such as distant filtering differences.

For broad wear/deposits use the sibling [surface-paint skill](../blender-threejs-surface-paint/SKILL.md). For UV/export auditing use [asset-pipeline](../blender-threejs-asset-pipeline/SKILL.md); for actual scene capture and diagnosis use [scene QA](../threejs-scene-qa/SKILL.md). The workflow above remains usable if these optional siblings are unavailable.

Runnable examples and their tested scope are in [evaluation](references/evaluation.md). The included two presets are examples, not art-direction defaults or a performance guarantee.
