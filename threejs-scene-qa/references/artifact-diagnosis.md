# Attribute a defect before changing the scene

Keep exposure, camera, viewport and filtering fixed. Capture one diagnostic change at a time, restoring production state between captures.

| Observation | Isolation | Investigate |
|---|---|---|
| Grain follows pigment and survives lighting-off | Albedo-only, no decals | Texture contrast, noise frequency, mask density and repetitions |
| Noise remains on neutral materials | Disable shadows, then GI separately | Shadow acne, bake sampling, geometry or lighting integration |
| Chroma blocks in neutral dark regions | Source image vs decoded compressed image with identical filtering | Encoding, codec quantization, alpha and color-space handling |
| Regular striations change with shadow switch | Shadows off, same lighting otherwise | Shadow bias, projection and texel size |
| Black bands/holes persist without normal maps or effects | Face IDs, wireframe/CPU rays, single-sided view | Overlaps, inward normals, missing faces, coplanar receivers |
| Borders appear at stochastic cells or split meshes | Known normal/height fixture, UV and mip views | Coordinates, derivatives, transformed tangent slopes, mismatched scales |
| Decals float or appear on the wrong side | Target IDs and source-triangle hit data | Depth, facing, clipping, stale geometry revision, wrong height profile |
| Texture appears flat where sand covers paving | Normal/roughness isolation | Pigment-only overlay versus full material response |

Do not blur albedo to remove GI Monte Carlo noise. Stable procedural seeding does not prove the grain is intentional: baked noise is also static. Do not darken surfaces to conceal codec problems or patch geometry defects with AO.

A meaningful final comparison uses the actual decoded maps and shader path. An uncompressed diagnostic with different mip/filter settings is not a clean codec comparison. Geometry repair may invalidate lighting beyond the edited faces; assess visibility and bounce changes.

For capture modes, albedo should remove illumination while preserving base artwork; neutral replaces material variation while retaining the lighting under test. Record the implementation because application-specific shader hooks cannot be disabled reliably through generic map=null assignments.
