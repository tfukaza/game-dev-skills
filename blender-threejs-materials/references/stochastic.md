# Regional sampling when repeating textures are visible

Use one deterministic field with overlapping regions, not random per-frame UVs or a discontinuous nearest-cell cutoff. `scripts/stochastic.mjs` contains a WebGL 2 GLSL implementation and dependency-free numerical reference. `scripts/stochastic_blender.py` builds its editable Blender node equivalent. Both offer `natural` and `courses` example presets. The latter retains frequency and allows only half turns; assess ghosted joints in the real material before choosing this technique for strongly structured textures.

## Runtime contract

Insert `GLSL` into the fragment shader after its common declarations. Use this sequence inside the existing physical-material path:

```glsl
SurfaceStochasticPatch p = surfaceStochasticPatch(uv, settings);
vec4 color = surfaceStochasticColor(colorMap, p, blend); // once: finalizes weights
vec4 orm = surfaceStochasticData(ormMap, p);             // reuse R/G/B
vec3 normal = surfaceStochasticNormal(normalMap, p, normalSigns);
```

`settings = vec4(cellSizeInUv, halfTurnsOnly, scaleJitter, colorGainJitter)`;
`blend = vec2(weightExponent, linearLuminanceInfluence)`. Color must be decoded to linear before computing weights. Maps share the same repeat UV frame and RepeatWrapping. Brightness changes color only. The normal function returns a decoded tangent normal; retain the host material's normal scale, TBN and lighting. No unique-paint coordinates change.

There are nine texture reads for color/ORM/normal. Derivatives come from continuous input UV before floor/hash/region selection. Each textureGrad receives the regional Jacobian times those derivatives; differentiating discontinuous sample UVs creates incorrect mips at joins. Hash modulo is explicitly nonnegative, including negative coordinates. The finite 251-cell hash period is not suitable for arbitrarily large worlds without assessing visible recurrence.

## Normal coordinate contract: measure, do not guess

For sample coordinates `u' = J*u + t`, a sampled surface gradient transforms by `transpose(J)`. Decode slopes `n.xy / max(n.z,.05)`, apply the source-V sign, transpose(J), then the output-TBN-V sign; blend slopes and normalize `(sx,sy,1)`. Do not blend encoded RGB as though rotated normals remained in the original frame.

`normalSigns = vec2(sourceVToLatticeV, latticeVToTbnV)`, each ±1. This example assumes runtime UV=(Blender U,1−Blender V):

| Verified convention | Signs |
| --- | --- |
| Blender +Y source with retained Blender tangent basis | (-1,-1) |
| Blender +Y source with TBN derived from flipped runtime UV | (-1,+1) |
| Source normals already in runtime UV basis, derived runtime TBN | (+1,+1) |

These rows are conditional examples. Inspect the exported tangent handedness and UV directions, or use the known-height fixture. A `USE_TANGENT` define alone does not establish which convention produced those tangents. Negative object scales/mirrored UVs need their own TBN validation. This surface-gradient blend has no absolute source height and does not add derivatives of blend weights as invented relief.

## Blender graph recipe

In a caller-owned material with explicit original UVMap node:

```python
from stochastic_blender import stochastic_material
outputs = stochastic_material(material.node_tree, uv_node.outputs['UV'],
    {'color': color_image, 'normal': normal_image, 'orm': orm_image}, 'natural')
# Connect outputs['color'] to Base Color.
# Separate outputs['orm']: G to Roughness, B to Metallic; handle AO according to lighting.
# Feed outputs['normal'] through a Tangent Normal Map node naming the same original UV layer.
```

Color images use sRGB; normal/ORM images use Non-Color. The group returns encoded normals in the Blender tangent basis and samples Blender images with reflected runtime V. It adds nodes but never deletes existing nodes, images or UV layers. One cached group shares three images across nine image nodes. The cache includes preset settings and image names, so changed settings create a new group while unchanged calls share it. Blender controls image filtering internally, so exact distant mip parity with textureGrad is not promised.

The approach is informed by [Heitz and Neyret's stochastic texturing](https://eheitzresearch.wordpress.com/722-2/) and [Mikkelsen's surface-gradient tiling treatment](https://jcgt.org/published/0011/03/05/). The included sharpened, color-aware blend does not implement their entire algorithms or require histogram-transform textures.
