# QA adapter helpers

Requires Node 18+ for tests; the helper is also a browser ES module.

```sh
node --test scripts/test-scene-probes.mjs
```

Import [scene-probes.mjs](../scripts/scene-probes.mjs) into a scene-specific diagnostic adapter.

- landmarkErrors(expected, observed, frame) compares named pixel coordinates against width/height-normalized tolerances. The caller supplies semantically correct landmarks. It does not infer geometry from an image.
- captureViews(adapter, options) saves state, restores before each view/mode, waits for readiness, renders/captures and restores in finally. Provide saveState, restoreState, setView, setMode, ready, render and capture. Capture can return a file path, bytes or metadata; output storage belongs to the adapter.
- lifecycleProbe(adapter, options) uses a warmed snapshot, then runs ready/fetch/decode disposal cycles. Provide snapshot, begin, waitForPhase, dispose and settle. Settle must await/drain all outstanding asynchronous work, including expected aborted promises, without resurrecting resources. The helper calls dispose twice to exercise idempotence.

Use explicit supported diagnostic modes (production, albedo, neutral, no-normals, no-shadows, no-decals, source-textures). Unsupported modes should fail rather than silently approximate. Implement feature toggles at the application's material/lighting extension boundary. Never remove unknown onBeforeCompile hooks blindly.

Apply bounded timeouts in the application test runner so stalled network/decode readiness becomes a reported failure. Test real capsule traversal in the application's own controller harness; generic landmark and lifecycle helpers cannot prove that behavior.

## Real browser fixture

The bundled [scene fixture](../fixtures/scene.html) constructs an unfamiliar bridge, lower passage, inclined approach and small prop group in Three.js. It exercises Octree/capsule contacts, upper/lower clearance, ramp heights, diagnostic captures and state restoration. It does not load or alter an existing application tab.

```sh
node scripts/run-browser-fixture.mjs --three-root /absolute/path/node_modules/three --playwright /absolute/path/node_modules/@playwright/test/index.mjs --output /tmp/scene-qa-output
```

Supply existing local dependencies. The runner opens a loopback-only temporary server and isolated Chromium, writes six images plus JSON to the chosen output folder, and closes both. Traversal uses a 1mm endpoint tolerance to accommodate capsule/triangle contact resolution. The renderer preserves its drawing buffer for screenshots, so the short RAF sample validates recording only, not production performance.

Adapter snapshots must be independent of live state. Lifecycle cleanup attempts disposal, settlement and idempotent disposal even if an earlier step fails, reporting all errors. Capture/benchmark cancellation is checked after final asynchronous callbacks as well as before starting work.
