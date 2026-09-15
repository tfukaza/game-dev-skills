---
name: blender-uv-textures
description: Unwrap and inspect actual Blender mesh UVs, export exact-resolution UV layouts, generate or fit surface artwork against those layouts, and verify explicit UV/material bindings on the model. Use for UV mapping and mapped textures independently of prop modeling.
---

# Blender UV textures

Work from the actual modeled mesh and intended UV channel. A diagram of plausible rectangles is not proof of a valid unwrap, and an attractive generated texture is not proof of correct mapping. For UV-only work on an existing approved mesh, do not initiate unrelated modeling or reference generation.

Follow [the UV workflow](references/uv-workflow.md): settle relevant geometry, mark seams/unwrap, inspect a checker in Blender, export the actual layout at the intended resolution, inspect it and identify the islands, supply it as the image-generation reference, inspect alignment, then reapply and examine the mapped model from multiple angles. When the user requests computer use, use the live Blender UI for the requested inspection and verification; scripts may assist but do not replace visible evidence.

Use the available image-generation tool/skill for original bitmap authoring. Keep layout guides separate from final unlit base-color artwork, with edge bleed and appropriate gutters. Image generation does not guarantee exact pixel registration; verify dimensions, island orientation and alignment rather than claiming pixel-perfect output.

Bind the intended UV channel explicitly and use correct color space/wrapping. Distinguish a repeating physical-scale tile from a unique packed atlas. If geometry or UVs change, refresh affected exports and alignment checks. Preserve source images/prompts, UV manifests and editable materials; pack textures or verify relative paths.

For canonical lettering use [surface graphics](../blender-threejs-props/references/surface-graphics.md); for decals/projection use [surface paint](../blender-threejs-surface-paint/references/decals-lettering.md). Use [asset pipeline](../../pipeline/blender-threejs-asset-pipeline/SKILL.md) only when runtime export is requested. Include actual mapped-model evidence in the [shared independent review](../blender-threejs-props/references/evaluation.md) for substantial asset creation/polish.
