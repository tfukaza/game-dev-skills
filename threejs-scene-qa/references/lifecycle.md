# Loading and lifetime verification

Use staged failure cases for manifest fetch, model/texture download, decode/transcode, shader preparation and final binding. An aborted request is not proof that all asynchronous work stopped.

For each case verify:
- Accurate fallback remains usable on failure; no partial generation mixes geometry, UVs, lightmaps or probes.
- Leaving the route prevents late results from attaching to a dead scene.
- Owned late resources are released, shared resources remain valid for live consumers.
- Disposal is idempotent and removes hooks, listeners, attributes, object URLs and owned bitmaps.
- Re-entering works, with stable placement IDs through LOD compaction and no stale probe/artwork assignments.

Warm renderer/loader caches before comparing resource trends. Exercise successful load/dispose and cancellation at multiple checkpoints, then remount. Track pending work, bindings, textures and geometry ownership; exact GPU residency may be unavailable. Counts can prove a regression trend but not total driver memory.

The helper orchestrates application adapters and compares counters to a supplied warmed baseline. Its tests use synthetic asynchronous resources; they do not replace the actual loader/controller or a device memory investigation. Use the asset-pipeline skill for implementation ownership rules.
