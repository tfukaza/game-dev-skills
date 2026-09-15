# Selected marks, lettering and geometry

Decals suit identifiable marks: a chosen crack, stencil, scuff, graffiti or particular stain. A large mural can be a valid decal; size alone is not the issue. General plaster or terrain character should remain when local decals are removed. Do not treat every surface as a clean base plus scattered interchangeable photographic stamps.

Use stable semantic targets and authored world positions/sizes. Project against actual target triangles with shallow depth; split across corners when needed. Choose outward-facing contacts, and for ground require an upward-facing normal plus agreement with the visible top elevation. A downward ray can hit a slab underside or another layer; a hit alone is not validation. Bind cached alignment to the raw geometry hash, target and original placement. Import the authoring-compatible raw GLB into Blender rather than assuming a runtime-compressed asset is a valid source.

Inspect the generated UV direction before mapping an atlas. For a top-left atlas with flipY=false and Three DecalGeometry's +Y→V1 convention, remap V as `v0 + (1-v)*(v1-v0)`. This formula is conditional on that verified convention. Soft grime may need blending with a low alpha threshold; crisp marks need the appropriate local edge treatment. Neither should open transparency through the underlying opaque wall. Let painted marks retain the base surface relief.

Distinguish the intended object:

- Painted lettering: apply the canonical image-generated artwork to surface color or an appropriate unique mask, usually an opaque baked material at delivery. Follow the [props surface-graphics workflow](../../blender-threejs-props/references/surface-graphics.md); do not silently replace it with a generic system font.
- Mounted sign: a physical sign surface with thickness, attachments and artwork.
- Raised/cast lettering: actual geometry when its silhouette or relief matters.

For baked labels, retain exact text and editable font/artwork sources, select eligible faces so text does not wrap onto unrelated backs/sides, and allocate enough atlas pixels for reading distance. Bake color with lighting excluded, preserve original PBR source, and inspect actual exported glyph orientation and spelling. Alpha used to composite ink does not require a transparent final prop. Do not delete existing UV layers simply because an isolated example reduces its own temporary projection layers to one final atlas.

The user's wording is authoritative; verify that the pixels in generated artwork actually spell it correctly, then make a targeted image revision if needed. Generated artwork may be the canonical visual design, but is not evidence of dimensions, topology or UV contracts. When existing approved fonts or explicit typography instructions call for deterministic typesetting, use shaping-capable rendering for Arabic and other shaped scripts; per-character Latin placement is not a generic multilingual solution.

The sibling asset-pipeline skill owns generic UV/GLB auditing and props covers component geometry. Keep this skill focused on surface meaning and authoring. Record source images, seeds, mask schemas, font choices and generator code so a saved-source reload can reproduce or edit the result.
