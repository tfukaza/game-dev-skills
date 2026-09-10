# Dedicated atlas and export

Choose an unused texture-coordinate channel; preserve the existing material,
unique paint and decal UVs. Channel 2 is the supplied rasterizer's default, not a
requirement for every application. Keep one atlas layout across lighting presets.
Record the UV channel, geometry/atlas hashes, rig and encoding in the manifest.

Unwrap proxies may weld coincident authored splits to make continuous charts,
but transfer only the new per-corner UVs back to canonical geometry. A tolerance
that works in a meter-scale scene is not universal. Retain original corner IDs
or a rigorously verified triangle/attribute mapping. Seams may require vertex
duplication; positions, normal/tangent values, earlier UVs, material assignments,
vertex colors, topology and node transforms must otherwise remain equivalent.
Use a dedicated glTF attribute auditor; this skill does not ship a general GLB
rewriter. Export an uncompressed static donor for numerical guide rasterization.

Check actual receiver faces. Internal caps, coplanar overlaps and closed gaps can
bake black regions on surfaces that should be exterior. Unique UVs cannot fix
incorrect geometry. Exclude hidden editable duplicates, collision proxies and
unused prototypes from transport, while keeping visible occluders and bounce
surfaces, including props and foliage.

Audit global triangle overlap, bounds, chart density and gutters. The helper's
texel overlap check is only a guard: it cannot prove subtexel/global UV validity.
Inspect low-resolution and grazing-angle mip sampling. A valid packing with
insufficient separation still bleeds. Packing chart AABBs can be conservative;
it is a tunable method, not a universal packing algorithm.

When receivers share a target, bake raw passes with margin zero. Per-object
dilation can overwrite another receiver's chart. Preserve authoritative bake
coverage independently from contact AO alpha, including covered black pixels.
After all transport is combined and filtered, call
`padded, expanded = pad_empty(rgba, coverage, steps)` from
`scripts/lightmap_io.py`. It returns copies, extends only empty pixels and never
wraps at image boundaries. Expansion cannot enlarge chart gaps or repair overlap.

Verify orientation using an asymmetric known-position fixture, not a symmetric
checker alone. The supplied donor default reflects glTF V into Blender's
bottom-up array order; runtime `flipY` must be selected with the actual loader
and delivery orientation. Saved sources must reload with exact UVs and packed
linear image values, including images not connected to a material output.
