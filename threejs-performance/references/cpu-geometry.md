# CPU, geometry, and visibility

Use this module after tracing application or submission cost.

- Reuse scratch vectors, matrices and typed buffers in measured hot loops. Avoid rebuilding static data, unnecessary matrix/material updates, and uploading unchanged instance buffers. Caches require explicit invalidation.
- Profile collision/picking broad phase and actual query counts. Choose appropriate spatial structures or simpler collision meshes; check controller behavior and update costs.
- Share compatible geometry/materials and instance repeated assets. Instancing reduces submission but still processes geometry and fragments. Preserve stable graphics, picking and lighting IDs when instance slots compact or detail levels change.
- Group by material within useful spatial chunks. Global merging can defeat culling. Recalculate transformed bounds and test chunk boundaries. Avoid a material clone per prop just for tint or artwork variation.
- Reduce geometry where it does not carry silhouette, deformation or close-view shape. Use detail levels with hysteresis and stable identity. Preserve large foliage crowns and cloth folds. Screen coverage can be more appropriate than a universal distance.
- Remove invisible geometry only after checking neighboring/traversal views, shadows, reflections and collision.
- Lower-frequency updates or render-on-demand suit unchanged content. Continuous gameplay still requires simulation, input and interpolation. Do not remove necessary updates to win a benchmark.
- Workers and WASM are candidates for demonstrated compute bottlenecks. Include serialization, transfer and synchronization costs. They do not directly fix GPU pixel cost.

Check [InstancedMesh](https://threejs.org/docs/pages/InstancedMesh.html), [BatchedMesh](https://threejs.org/docs/pages/BatchedMesh.html) and [rendering on demand](https://threejs.org/manual/en/rendering-on-demand.html) against the installed version.
