# Prop contracts

## Physical and visual decisions

Define the model's real-world size and pivot independently from its library arrangement. Preserve the exporter root's coordinate conversion when placing it in Three.js. Baking transforms into vertices and also applying them to the instance doubles the transform.

Choose support samples that belong to the actual base, feet or leaning edge. For a rigid object on a locally planar slope, use the receiving normal and intended orientation to establish contact, then verify the transformed samples. A curved slope can leave legitimate gaps away from the contact patch. A mean height adjustment alone can leave one side buried. Collision bounds and visible base geometry can differ intentionally, so inspect both with their actual purposes in mind.

Variation should have a stable identity and physical reason. Separate construction parameters from graphic selections; keep a variant's dimensions and artwork consistent across LODs. Do not seed from array index, mutable iteration order or per-frame randomness. New variants need not add new materials if shared atlases, vertex data or instance parameters express the intended differences. Read [performance](../../threejs-performance/SKILL.md) before trading away the requested appearance for an assumed speed gain.

For the preferred image-generated artwork workflow, read [surface graphics](surface-graphics.md). Flat lettering belongs in the printable surface's UVs. Use a real plaque mesh when the object has a plaque; use geometry for embossed text only when relief is visibly required. Retain editable artwork and compare its orientation, legibility and material response on the exported prop. Image generation is preferred for new bitmap artwork; a procedural gradient is not an automatic substitute for a requested label or motif.

## Helper input and limits

Run from the skill folder:

```sh
python3 scripts/prop_contract.py variants path/to/variants.json
python3 scripts/prop_contract.py audit path/to/export-facts.json
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

The variants input is:

```json
{"seed":"yard-v1","ids":["crate-a","crate-b"],"ranges":{"uniformScale":[0.98,1.02],"dentDepth":[0,0.025]},"choices":{"graphic":["stencil-a","label-b","bare"]}}
```

Each ID and parameter has its own hash stream. The helper produces parameters only; the author must apply them consistently to geometry, collision and graphics. It never changes the scene or writes files.

The audit consumes **vertex facts from the actual export**, not trusted declared bounds. This compact format lets a DCC/runtime adapter provide the facts without coupling the helper to a particular exporter:

```json
{
  "units":"m",
  "assets":[{
    "id":"crate", "dimensions":[2,1,1], "pivot":"bottom-center",
    "boundsTolerance":0.02, "pivotTolerance":0.005, "requiredLods":[0,1,2],
    "lods":[{
      "level":0, "positions":[[-1,0,-0.5],[-1,0,0.5],[1,0,0.5]],
      "indices":[0,1,2], "normals":[[0,1,0],[0,1,0],[0,1,0]],
      "uvs":{"uv0":[[0,0],[0,1],[1,1]]},
      "tangents":[[1,0,0,1],[1,0,0,1],[1,0,0,1]],
      "surfaceIds":["wood","label"], "appearanceKey":"crate-red-v2"
    }]
  }]
}
```

The abbreviated triangle above explains the schema; it is not a passing crate fixture. The tests construct complete compact examples in memory. Each LOD may include a glTF-style column-major affine `matrix` mapping its positions into the declared asset-local frame. Bounds use **referenced vertices**, so unused vertices cannot conceal a shrunken LOD.

Required channels and semantic/appearance identities come from the first LOD and must survive later levels. Normal/tangent vector magnitudes, array lengths and finite values are checked; UV coordinates may tile outside 0–1. Triangle count may stay equal or decrease. `dimensions`, bounds tolerances and the optional bottom-centred pivot are checked independently for every level. Other pivot conventions use `pivot:"custom"` and require task-specific support validation.

This helper does not parse GLB, prove watertightness, compare texture pixels, validate collision, or establish silhouette/lettering quality. An export adapter's facts must be accurate; use [asset pipeline](../../blender-threejs-asset-pipeline/SKILL.md) for direct GLB auditing and [layout](../../blender-threejs-layout/SKILL.md) for the receiving surface/contact helper. A passing bounds check cannot prove two meshes look alike. In particular, an unchanged appearanceKey cannot prove that lettering UVs remain undistorted across different LOD topology; inspect corresponding surface artwork in the rendered models.
