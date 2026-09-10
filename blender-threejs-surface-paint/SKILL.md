---
name: blender-threejs-surface-paint
description: Author layered environmental wear, sand or dirt deposits, repairs, surface markings and lettering for Blender assets delivered through Three.js. Use geometry-aware masks for broad weathering and selected decals for local marks, preserving editable paint and coherent material properties.
---
# Contextual surface paint

Broad wall and terrain weathering should come from a layered material/mask system, not an accumulation of interchangeable crack or hole image stamps. That system may bake to ordinary textures; it does not require expensive runtime procedural weathering. The distinction is an effect's role and distribution, not its file extension.

1. Read the current reference/layout contract. Identify the intact material, exposure/repair layers, deposit sources, traffic and protected areas. If geometry is changing, work on reusable materials while deferring final unique masks/projector alignment until their anchors are stable.
2. Author large distributions using ground profiles, ledges, fixtures, recesses and chosen wear regions. Add multiscale breakup within and around those regions. Use surface-specific shape models and preserve quiet areas. Keep physical scale and contrast independently controllable.
3. Blend relevant material properties with the same layer masks. Exposure changes grain/roughness; repairs alter grain and relief; dense deposits can bury base color, normal relief and cavity response. Keep intact walls opaque and illumination out of pigment. Read [layers and masks](references/layers.md), including the runnable contextual-mask example.
4. Add deliberately located marks after the underlying surface conveys age. Read [decals and lettering](references/decals-lettering.md) for placement, painted text and physical signs. Real holes or silhouette-changing chips need geometry when visible at the intended distance.
5. Inspect both masks and actual materials at overview and walking scale, with local decals removed and under relevant light directions. Use the sibling [scene-QA skill](../threejs-scene-qa/SKILL.md) to separate intentional wear from lighting/compression errors. Save generated baselines separately from manual overrides: refreshing context should move procedural wear while retaining unrelated edits. The example's default preserves the active image; `--refresh-context` rebuilds underneath manual pixels and `--reset-manual` explicitly discards those overrides after a backup.

For repeating PBR/stochastic sampling use [materials](../blender-threejs-materials/SKILL.md); for export/UV audits use [asset-pipeline](../blender-threejs-asset-pipeline/SKILL.md). Optional siblings supply deeper tools; this workflow does not require loading all of them. [Evaluation](references/evaluation.md) records the example's tested behavior and limits.
