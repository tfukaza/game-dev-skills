---
name: blender-threejs-baked-gi
description: "Bake calibrated diffuse lighting in Blender Cycles and deliver it to a Three.js scene, including lightmap atlases, linear I/O, guarded denoising, compression and optional static-prop probes. Use for actual bounced-light workflows, not ordinary albedo texture baking or AO-only effects."
---

# Cycles to Three.js baked GI

Start by identifying the installed Blender/OCIO and Three versions, canonical
geometry, existing UV/material channels, lighting presets and delivery budgets.
Choose a transport contract before baking. The tested hybrid contract stores
sky direct + indirect and solar indirect, leaving direct sun live at runtime.
Do not silently substitute AO or a flat ambient color for GI.

Preserve these invariants: linear raw transport remains recoverable; receiver
albedo is not multiplied into a lighting-only map; lighting contributions are
counted once; existing geometry/material attributes survive atlas transfer;
coverage is independent of AO; geometry, maps and probes belong to the same
published revision. Samples, atlas sizes, codecs, denoiser thresholds, probe
density and artistic lighting are tunable choices, not universal constants.

Use the references only for the current stage:

- [Transport and runtime integration](references/transport.md): pass selection,
  unit calibration, EXR I/O, shader adaptation and asynchronous lifecycle.
- [Atlas and export](references/atlas.md): dedicated UVs, attribute preservation,
  receiver geometry, coverage, gutters and global padding.
- [Denoising](references/denoise.md): the NumPy helper, guide conventions,
  outlier filtering, CLI and supported input boundaries.
- [Encoding and compression](references/compression.md): measured range,
  codec comparison, mip sampling and budgeted tiers.
- [Static prop probes](references/probes.md): optional real-radiance SH capture
  while preserving instancing; this is an adapter recipe, not a drop-in pipeline.
- [Late repair](references/late-repair.md): diagnose artifacts, preserve raw
  checkpoints and bound a selective rebake only when its transport assumptions hold.
- [Evaluation](references/evaluation.md): executable tests, recorded results,
  version limits and remaining application-level checks.

Progress from a tiny calibrated fixture and a representative pilot to final
transport, filtered/encoded candidates, runtime review, then matching publication.
A fixture that compiles with substitute maps proves integration only. Final
appearance and performance require the actual delivered geometry and textures.
Keep editable source/material graphs and packed linear images reloadable.

Prefer an isolated background Blender process writing a new workspace for
repeatable fixtures. Do not repurpose a user's open scene or application-wide
preferences. Reuse expensive raw passes only after validating their source,
atlas, rig and sample metadata. Report failed checks and measured limitations;
do not compensate for an unexplained artifact by changing exposure or fidelity.
