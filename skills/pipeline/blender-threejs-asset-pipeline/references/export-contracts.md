# Export contracts

## Define the transition

Distinguish editable source components, visible runtime receivers, collision, prop prototypes/instances and authoring helpers. A hidden collection can still be exported by a broad selection rule; set membership deliberately. Use a clean isolated process for candidates rather than resetting a user's unrelated Blender window. Do not save global preferences as part of an asset operation.

State the coordinate conversion and units once. Preserve root transforms or bake them once into vertices; do not do both. Nonplanar top faces require the same explicit triangles in Blender, collision and procedural Three.js geometry. Check resulting normals/tangents after modifier application and export. A stored `TANGENT.w` sign is meaningful, especially under mirrored UVs.

Semantic IDs outlive material joins and mesh renaming. A merged surface can carry all contributing aliases. Preserve metadata used for collision, paint receivers, instance identity and runtime bindings. An asset may have repeated tiled UVs, a unique painted UV set and a lightmap UV set; record each role and texture channel mapping instead of assuming that Blender layer order alone guarantees export.

For LODs, preserve the pivot, physical bounds, appearance identity and required channels while allowing topology and UV sampling to change intentionally. Use [props](../../../authoring/blender-threejs-props/SKILL.md) for the library contract. Keep compatible shared images external or otherwise deduplicated without changing how they bind to materials.

## Narrow updates and repairs

Prefer a candidate copy and an explicit delta when repairing an approved source. An attribute-only change should preserve every original contributing corner value and material assignment, even if the exporter splits vertices or reorders triangles. Comparing raw accessor indices or vertex counts alone is insufficient.

For geometry changes, identify original and resulting faces, the reason, and unchanged areas. Interpolate new corners within their source triangles, including all relevant UVs, normals, tangents and colors. Test winding and tangents where interpolation changes their meaning. Do not silently broaden tolerances to make a parity failure pass. If a DCC re-encodes a bounded normal difference, document its exact scope and effect separately from unchanged runtime data.

A lighting repair may require newly exposed surviving faces as well as modified faces. Preserve the atlas when feasible, mark the receiver subset, retain unselected occluders without duplicates, and clear removed coverage before merging replacement transport. The actual bake workflow belongs to [baked GI](../../blender-threejs-baked-gi/SKILL.md).

The bundled auditor intentionally does **not** approve arbitrary geometry deltas. Use it on unchanged partitions or a separately reviewed corrected baseline, with a changed-face ledger. A passing comparison against a corrected baseline must not be reported as preservation of the original scene.

## Streaming and resource lifecycle

Give geometry, materials, textures, decoded image bitmaps and per-instance attributes explicit owners. Sharing a source buffer is different from cloning a mutable material or owning a new instance attribute. Preserve immutable data; dispose shared resources only when their owner is done.

Check cancellation after asynchronous boundaries, including response parsing, decoder completion and dependent loads. An aborted operation may still complete and allocate objects; collect and dispose those late results. Ensure external images inherit the task's request lifetime instead of escaping through a loader's private requests. Revoke temporary object URLs after parsing.

Install dependent material changes atomically after the required maps/data validate. A partial preset failure should retain a working fallback and release the successful partial decode. A later unlit object must not downgrade already configured objects. Preserve prior shader hooks/cache keys and restore them during disposal. Handle disposal idempotently.

Validate repeated enter/leave, leave during loading, missing optional resources and incompatible revisions. Check actual resource trends when investigating memory; a unit test counting `dispose()` calls alone does not prove GPU memory stability. Measurement belongs to [performance](../../../validation/threejs-performance/SKILL.md).

## Publication evidence

Associate the candidate with the layout/asset revision and exact dependent content hashes. Verify the files referenced by the delivered manifest, not a nearby candidate with the same filename stem. Match textures, UV metadata, lighting and per-instance data to that same revision. Runtime fallbacks should remain usable on missing or stale optional data.

Report source path, candidate and delivered hashes, supported preservation checks, intentional deltas, tests and remaining appearance limits. Keep automated evidence distinct from visual acceptance. Inspect the rendered packaged result; neither lossless buffer checks nor a successful source preview certifies the complete delivery.
