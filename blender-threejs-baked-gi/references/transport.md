# Transport, units and runtime ownership

For the tested hybrid contract:

| Pass | Illumination | Cycles bake filter |
| --- | --- | --- |
| Sky transport | Calibrated world; sun disabled | DIFFUSE, DIRECT + INDIRECT, COLOR absent |
| Solar bounce | Sun; world black | DIFFUSE, INDIRECT, COLOR absent |
| Optional contact AO | Distance-limited visibility | Separate data, never a GI replacement |

Add the two diffuse RGB buffers in scene-linear space. Other surfaces retain
their albedos so bounced light carries color. Excluding the receiver's albedo is
different from whitening every bounce surface. Decide whether receiver geometric
or shading normals belong in the bake; avoid unintentionally applying repeating
normal detail twice. Restore all temporary material links before saving sources.

Run `scripts/blender_calibration.py` in a new output directory. In the tested
Cycles version, unit sky radiance produces 1 and unit normal-incidence sun
produces 1/pi in the color-disabled diffuse pass: stored L = E/pi. Encoding
`sRGB(L/R)` therefore needs `R*pi` after sRGB decoding to supply irradiance E.
The isolated solar INDIRECT pass must remain zero. Recalibrate on a different
render/version contract instead of copying the multiplier blindly.

`scripts/lightmap_io.py` provides `float_image`, `image_pixels` and
`save_linear_exr`. It explicitly writes FLOAT RGBA ZIP OpenEXR and restores
render-output settings. Tagging already gamma-encoded pixels as linear cannot
repair them. The regression fixture independently tests RGB through HDR 8 and
fractional alpha under Standard and AgX, then packs/saves/reloads a float image.
Choose the actual installed scene-linear OCIO name; the supplied fixture uses
Linear Rec.709. Keep raw EXRs separate from filtered and display-encoded files.

Three.js integration is application-specific. Inspect the installed
`ShaderChunk/lights_fragment_maps`, `lights_fragment_begin`,
`lights_physical_pars_fragment` and `SphericalHarmonics3` sources. In the tested
MeshStandardMaterial path, lightMapIntensity multiplies decoded RGB irradiance.
Set the selected UV channel explicitly and ensure image/UV orientation agrees.
Replace existing ambient/hemisphere/IBL **diffuse** fill for successfully bound
receivers; retain live sun direct diffuse/specular and environment specular,
including multiscattering. Removing all IBL irradiance code can damage specular
energy. Compose existing material hooks, assert expected shader anchors, use a
versioned program-cache key, and GPU-compile representative materials.

Loading recipe: validate scene/atlas revision and encoding; fetch/decode both
presets; bind only when all succeed and receiver UV/revision matches. Switch
presets atomically. On failure retain the earlier response; on abort release
late textures/bitmaps and prevent installation. Dispose in reverse ownership
order, restoring original maps, intensities, hooks and cache keys exactly once.
Do not dispose shared model textures merely because a lightmap controller ends.

Primary references: installed source is authoritative for shader hooks;
[Cycles baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)
documents pass selection, and [Three color management](https://threejs.org/manual/en/color-management.html)
documents texture/working/output color spaces.
