# Optional static-prop diffuse probes

Use probes when repeated static props must retain instancing and shared material
UVs. This reference is an adapter recipe. Implement against the application's
scene builder, loader, LOD system and installed Three source; no generic capture
or shader adapter is shipped here.

Capture after final architecture and lightmaps are reviewed and stable. Build the
actual scene, await asset/lightmap readiness, and validate source hashes before
and after capture. For each receiver, temporarily exclude **all** its instance
parts, capture at a meaningful point, and restore exact matrices in `finally`.
Other geometry stays present. A center-of-visible-bounds probe is a starting
choice; large props spanning a sharp light boundary need more spatial samples.

Capture linear HDR radiance with no exposure, tone mapping or fog. A calibrated
capture environment must match the bake; an art-directed display panorama can
have unrelated energy. Match the actual sun, shadows and specular environment.
Do not feed an old ambient diffuse approximation back into the capture. A single
pass with baked architecture and direct/specular neighboring props approximates
higher-order prop-to-prop transport; describe that limit rather than claiming a
converged all-object solution. Never substitute AO-scaled flat ambient colors.

Three's installed `LightProbeGenerator` integrates a cubemap into L2 radiance SH.
Nine RGB coefficients are 27 floats; a convenient padded packing is seven RGBA
texels per receiver/preset. Keep finite float32 values and declare basis, order,
color space and revision. Evaluate the cosine convolution **once**, in the same
world frame as the normal-mapped fragment normal. An irradiance SH dataset would
need a different contract. Test a constant radiance field and a known directional
case against `SphericalHarmonics3`, not merely shader source strings.

A shared coefficient DataTexture and compact per-instance index preserve batching.
When LOD batches compact slots, move the placement's probe index with its matrix.
Keep preset switches atomic, restore hooks/attributes on disposal, and release
late downloads without reactivating disposed materials. Validate every placement
ID, coefficient count/bytes and source hash, not just the number of objects.

Seven fragment fetches looked avoidable, but an experimentally equivalent vertex
fetch/flat-varying implementation had exact framebuffer parity and no repeatable
performance benefit. Do not adopt it by instruction. Measure real hardware with
matched views/DPR and reversed paired order. If experimenting, account for flat
versus smooth varying packing, authored tangents, map UVs, vertex colors, shadows
and device limits; retain a supported fallback. Preserve per-pixel normal detail.
