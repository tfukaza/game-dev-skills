# GPU materials, lighting, and pixel cost

Count main color, shadows, reflection/capture and postprocessing separately. Main-pass draws omit other work. Mark invalidation spikes separately from steady frames.

## Materials

Procedural anti-repetition may add no downloads but multiply samples and ALU work. Reuse packed-channel samples only when coordinates, gradients, filtering and interpretation match. Moving fragment work to vertices adds varying/interpolation pressure and is not automatically faster.

Bake static authoring layers when runtime editing is unnecessary. Preserve editable graphs/masks and the required color, roughness and normal response. Inventory shader variants; do not recompile materials every frame.

Match texture detail to screen footprint. Use mips and appropriate anisotropy at grazing angles, within measured cost. Diagnose derivative discontinuities before lowering quality; consult the material skill for stochastic normal correctness.

## Lighting and effects

Choose static lightmaps, probes and live lighting according to mobility and quality. Count contributions once. Baking shifts costs to storage, sampling and authoring; it is not free illumination.

Cache static shadows and captures; invalidate when relevant casters, lights, LOD or geometry change. Fit shadow coverage and resolution to needed receivers. Permanently frozen shadows are incorrect with moving inputs.

Inspect foliage/card overlap, transparency, double-sided rendering and shadow casting. Cutout alternatives change edges and antialiasing; evaluate rather than apply globally. Preserve intended density and silhouette.

Measure reflections, ambient occlusion, multisampling, render-target resolution and postprocessing separately. Diagnostic resolution sweeps reveal pixel sensitivity; undisclosed lower DPR is not same-quality optimization.

Compare source and actual decoded textures with matching filtering. A lower-resolution high-quality codec can beat a larger badly quantized texture visually. Choose with quality, bytes and residency evidence, not nominal resolution.
