# Portable performance helpers

Requires Node 18+ for CLI/tests; benchmark.mjs is also a browser ES module. No package installation is needed.

Run from this skill directory:

```sh
node --test scripts/test-performance.mjs
node scripts/inventory.mjs /absolute/path/inventory.json
```

## Benchmark adapter

Import `recordFrames`, `summarizeFrames`, `runABBA` from [benchmark.mjs](../scripts/benchmark.mjs). The ABBA adapter supplies saveState/restoreState, setVariant, ready, warmup, measure, conditions and checkQuality. measure returns increasing RAF timestamps; recordFrames supplies real browser sampling. Every method can be async. Abort propagates and restoration runs in finally.

conditions contains viewport, drawingBuffer, camera, preset, device, sceneRevision; add browser, power state and invariant quality fields. It must exclude the one deliberately varied factor, which must be named in the experiment report. Do not hide other quality changes. checkQuality returns an explicit boolean based on actual image/gameplay acceptance; frame equality alone is not traversal validation.

Store raw returned runs alongside the comparison. The classifier is a tolerance-based consistency guard, not a statistical confidence test. It refuses changed controlled conditions or a failed visual check. Application-specific readiness, shader preparation, target-device setup and optional disjoint GPU timers remain adapters; this module does not invent them.

## Inventory input

[Inventory helper](../scripts/inventory.mjs) accepts:

```json
{
  "files": [{"url":"https://example.test/atlas.ktx2","bytes":90000}],
  "resources": [
    {"id":"atlas","kind":"texture","width":1024,"height":1024,"levels":11,"faces":1,"layers":1,"format":"bc7"},
    {"id":"mesh-vertices","kind":"buffer","bytes":24000},
    {"id":"msaa-color","kind":"renderbuffer","width":800,"height":600,"samples":4,"format":"rgba8"}
  ]
}
```

List the actual transcoded format (e.g. bc7), not a container or encoder (KTX2/UASTC). Use format unknown when unavailable; the report remains explicitly incomplete. Supply all resolve/depth attachments as separate resources. Files deduplicate by canonical URL; resources by stable ID. Conflicting definitions fail. The result is logical payload, not an exact driver residency measurement. CPU decode peaks require separate measurements.

Supported formats and validation are in the small source table. Extend with tested block dimensions/byte sizes when necessary; do not guess unsupported formats.
