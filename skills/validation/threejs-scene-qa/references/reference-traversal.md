# Reference, assembly, and traversal checks

## Visual comparisons

Use authoritative maps/sections for topology and elevation, perspective imagery for composition and material character, and generated views only as inferred support. Do not interpret tactical-map shading as surface albedo.

Freeze camera transform, projection/FOV and viewport before comparing named landmarks. The landmark helper reports normalized frame-axis errors; it cannot determine which edge is semantically correct or whether depth/overlap matches. Numeric agreement is only one part of visual review.

Compare silhouettes and overlaps, foreground/background spacing, material boundaries and adjacent viewpoints. Start with a clay pass, then a representative material/asset, then the final encoded scene. Check that removing rejected architecture also removes its fallbacks and collision.

At walking height inspect ground/wall contacts, cracks at corners, coplanar flicker, attached supports, foliage roots, canvas folds, lettering registration, normal-map direction and texture scale. Check both lighting presets when present. Disable local decals once: aged surfaces should still have their intended broad wear.

## Actual controller

Test the application's real capsule/controller against both fallback and delivered collision: route transitions, slopes, bridge upper/lower paths, ceilings, intentional drops, stairs with collision ramps, jumping and settling beside cover. Rays and bounding boxes do not replace these tests.

Test joints at interior triangle locations, not only corners; Blender and runtime may triangulate a nonplanar quad differently. Sample shared borders and derivatives for ground/curbs. Rotate complete assemblies and recompute prop contact from exported bounds/support anchors.

Preserve movement speed, eye height, input controls, touch/pointer fallback and intentional unreachable boundaries unless the user requested a change. Verify appearance and collision independently: a traversable invisible gap is still a defect.
