# Integration and artifact diagnosis

Write down the actual contract before modifying a material: UV channel purpose, texture orientation, color space, tangent source, physical repeat scale, owned/shared resources and exported receiver tags. UV0/UV1/UV2 are common allocations, not universal names. For a top-left atlas with flipY=false, verify both the Blender export's V reflection and the consumer's generated UV direction. Do not apply a facade's unique-paint projection axes to perpendicular repeating faces: it can collapse coordinates and invalidate normals.

Keep source/runtime arithmetic aligned for pigment, roughness, normal response and shallow relief. Engine lighting need not be pixel-identical: Blender transport and Three's environment/AO treatment differ. Validate known surface values before judging lit screenshots. A data texture's alpha channel can be a mask; that does not imply material transparency.

When integrating with Three, preserve existing onBeforeCompile behavior and provide a program cache key for compile-time variants. Load shared channel sets atomically; retain the original material on failure. Abort pending requests, dispose resources exactly once and restore only the bindings the controller owns. Do not clone texture objects merely to choose a UV channel without considering sharing and lifecycle. Consult the current installed Three source when extending shader chunks; do not copy a version-specific replacement blindly.

## Desired variation versus rendering noise

Intentional variation has an authored scale, distribution and material meaning. Stable seeding is necessary for reproducibility but insufficient for quality: baked Monte Carlo errors are also static. When the result looks noisy, keep exposure fixed and isolate one layer at a time:

- Remove local decals; then inspect base color without lights or tone mapping.
- Use a neutral material with the actual lighting. Separately disable normal perturbation or shadow maps if indicated.
- Compare uncompressed source and delivered codec with matching filtering/color space. Lower nominal resolution with a better codec can outperform a larger map with colored block artifacts; measure and view, do not assume.
- Inspect actual geometry at dark seams; coplanar faces and holes cannot be repaired by changing pigment.

Do not simultaneously darken albedo and change exposure. Do not blur surface grain to hide GI noise. Use the sibling scene-QA and baked-GI references for capture and transport-specific diagnosis. Preview and source files do not prove that the delivered WebGL path works. Measure draw cost, texture reads and whole-asset bytes in the destination project rather than inheriting fixed budgets from this example.

## Appended assets and packed images

For appended assets, audit shader driver target IDs and include their control objects in the delivered collections. A constant driver expression can still evaluate incorrectly when its variable target is missing. Check the first render after reopening; later renders may hide initialization failures. Packed images can report undecoded pixel data before lazy loading, so inspect the packed payload independently of decoded availability. Preserve image color-space, alpha and material-slot assignments when deduplicating byte-identical images.
