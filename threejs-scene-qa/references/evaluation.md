# Executed scene-QA evaluation

Recorded 2026-09-10 with Node 24.12.0, Three.js 0.185.1 and isolated headless Chromium.

```sh
node --test scripts/test-scene-probes.mjs
```

Eight tests pass for landmark missing evidence, mode/state restoration, late decoder settlement, leak detection, initial/final cancellation, immutable snapshots, and preserving all phase/cleanup failures. Independent fresh adapters found and verified fixes for skipped settlement after disposal failure, mutable history, and cancellation during the final capture. The performance suite owns the corresponding final-quality-callback fix.

## Actual browser fixture

Run [the local browser fixture](tools.md) with explicit Three.js and Playwright dependency paths. The recorded run:
- Traversed below the bridge with an Octree capsule and less than 0.1m transient rise.
- Settled on the upper bridge surface at 3.000000003m.
- Detected a downward ceiling contact.
- Sampled the ramp at 0.6, 1.2, 1.8 and 2.4m.
- Captured six overview/underpass production/neutral/no-shadow images.
- Restored camera/material/shadow state and produced no page errors.
- Recorded real RAF timestamps without claiming target-device performance.

An initial endpoint assertion used a 1-micrometre tolerance and failed on an 86-micrometre lateral contact adjustment. The final fixture uses an explicit 1mm physical tolerance; the route and collision geometry were unchanged. Numerical and visual inspection confirmed the passage and ramp. [Recorded results](../fixtures/browser-results.json); [overview](../fixtures/overview-production.png) and [underpass](../fixtures/underpass-production.png).

## Independent scope checks

Fresh contact, prop and GLB fixtures accepted supported inputs and rejected wrong-floor/floating contacts, scale/artwork-key/tangent drift, UV edits and unsupported compression. Metadata and bounds cannot certify lettering pixels or cross-LOD UV registration; those remain rendered checks.

Discovery review routed ordinary font/LCP work outside these game skills, narrow crate movement to direct/contact work, and GI compression artifacts to targeted codec/lighting isolation rather than a full rebuild.

These fixtures do not establish the current game's visual fidelity, mobile hardware performance, image-generated artwork quality, all controller/input behaviors or arbitrary loader correctness. Apply the same evidence workflow to the actual destination application.
