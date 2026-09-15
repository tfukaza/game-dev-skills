# Layered wear and deposits

Use three independent controls: broad placement, intermediate fragmentation and fine material grain. Geometry and art direction establish where change belongs; noise varies its coverage. Plaster coating loss, troweled repair, asphalt abrasion and paving deposits should not share one generic blob silhouette. Connected wear can be locally interrupted and overlap in thin remnants; avoid a uniform full-width band or equally dense isolated chips. Reduce chip density above contact zones and preserve quiet intact material.

Deposits need variable density throughout their interiors, not only an irregular border. A domain-warped 2D density field combined with distance to walls/protected regions can produce branching peninsulas, isolated grains and thin coverage. Whether sand follows joints is a reference/physical choice, not a global rule. A clear walking lane is appropriate only where the scene implies traffic. Keep edges crisp enough for the material while breaking them with grain and chips; an evenly wavy outline or dark relief contour is not sufficient.

A compact contract for a unique surface includes a stable ID, world bounds, projection axes, physical extent, atlas rectangle, contact profile, fixture anchors and geometry revision/hash. Derive contact profiles and road/curb paths from the same geometry used for visible surfaces. Express feather widths and relief in metres. Clip all authored masks to their atlas region and allocate texel density by meaningful features rather than equal rectangles for unequal surfaces.

## Full material blending

For a coverage mask m in linear data space, blend linear color and roughness with m. Blend normals in a consistent tangent/surface-gradient basis, then normalize; do not mix normals from independently rotated frames. A deposit's own color grain, roughness and gentle normal replace the base as coverage grows. If it fills cavities, interpolate the cavity response too; do not double-occlude GI that already includes visibility. Coating exposure and repair may have different signed height responses. Keep relief restrained enough to avoid a uniform dark outline.

A wall's exposure mask reveals another opaque material, not the sky behind it. Broad weathering is neither a baked shadow nor a transparency cutout. Large damage that changes the silhouette belongs in geometry. User-directed stylization can override typical weathering; preserve explicit choices.

## Runnable example

From this skill directory (Python 3 and Pillow):

```sh
python3 scripts/context_masks.py fixtures/wall.json /tmp/wall-mask.png --size 256
python3 scripts/context_masks.py fixtures/ground.json /tmp/ground-mask.png --size 256
python3 scripts/test_context_masks.py
python3 scripts/fixture_refresh.py /tmp/paint-refresh-example
```

The supported JSON fields are `kind`, `seed`, `worldMeters`, plus `baseProfile`, optional `repairs` and `drains` for walls; or `walls`, optional `spreadMeters` and `clearLane` for ground. Unknown top-level context fields raise an error during generation/refresh. Wall drains use `anchor: [x,y]` in wall metres and optional `radiusMeters` (default .06), `lengthMeters` (1.2) and `strength` (.65). They generate broken downward grime below the outlet, clipped at the contact profile. They are a local art-directed runoff example, not a drainage simulation or a ground-drain adapter.

Output is RGBA data: R deposit, G exposure, B repair, A grime. Load it as Non-Color in Blender or NoColorSpace in Three; alpha is not surface opacity. `*-preview.png` illustrates all four channels on a flat pigment response, including retained manual edits after refresh. It does not prove a 3D material's roughness or relief.

Initial generation also saves `*.generated.png` (procedural baseline), `*.manual.png` (manual RGBA values), `*.manual-coverage.png` (binary pixel override) and `*.layers.json` (registration and baseline hash). Keep these together. Paint the active mask normally; `--refresh-context` detects pixels changed from the previous baseline/manual composite, retains those exact RGBA values as overrides, then regenerates only the context below them. Existing overrides persist across repeated refreshes, including zero-valued channels. Override coverage is separate from the mask's data alpha. This compact helper preserves whole pixels, not independent channel strokes or brush history.

```sh
# After painting /tmp/wall-mask.png and moving a drain/profile in the JSON:
python3 scripts/context_masks.py fixtures/wall.json /tmp/wall-mask.png --size 256 --refresh-context
```

The default still preserves an existing active file byte-for-byte without refreshing its preview. `--reset-manual` (legacy alias `--regenerate`) explicitly discards all manual overrides, regenerates the paint and saves a hash-named backup of the old active mask. A refresh refuses missing/modified baselines or changed resolution, extents or surface kind; it cannot safely infer old procedural paint from a flattened image or reproject edits to a changed coordinate system. Keep the generated baseline intact and edit the active image, not the sidecars independently. To migrate an older flattened mask, retain it and explicitly author an override layer against its known original baseline; do not label all old procedural pixels as manual by guessing.

The helper uses no NumPy or AI generation. Its `blend_properties` function illustrates coherent color/roughness/normal endpoints, but production layers need actual PBR maps and the correct tangent basis. It is not a universal weathering simulator, mesh projector, or final normal bake.

The geometry-aware placement approach follows the principles in [Adobe Painter Dirt](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/effects/generators/dirt); complete property blending is described in [Epic's layered materials](https://dev.epicgames.com/documentation/en-us/unreal-engine/layering-materials-in-unreal-engine). These references inform choices rather than impose another application's workflow.
