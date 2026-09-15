# Profiling and experiment design

| Cost | Evidence | Useful isolation |
|---|---|---|
| CPU simulation | Physics, animation, callbacks, allocation/GC, collision | Pause simulation while retaining the same rendered scene |
| CPU submission | Traversal, matrices, render lists, state changes, driver work | Bounded spatial batches at the same view/detail |
| GPU geometry | Vertices across passes, deformation, vertex shaders | Detail changes preserving pixel work |
| GPU pixels | Resolution, overdraw, shader samples, effects | Diagnostic resolution sweep or neutral material |
| Loading | Dependency waterfall, unique transfer bytes | Cold/warm cache with identical assets |
| First use | Decode, transcode, upload, compile, initial captures | First interaction separately from warmed frames |
| Memory | Buffers, actual GPU formats, mips, cube faces, targets | Repeated load/cancel/dispose/remount |

Isolation suggests hypotheses and can move the bottleneck. Confirm with targeted evidence. Time around render submission is not GPU duration. Use asynchronous timer queries where supported and discard disjoint samples. Readbacks, synchronous queries and excessive instrumentation can create stalls.

Record browser/version, GPU when exposed, physical vs emulated device, power/thermal state when known, CSS viewport, render DPR, drawing buffer, camera/projection or route, preset, quality, revisions and loading state. Disclose unavailable fields.

Measure readiness and first-use stalls before warmed steady-state. A short warm-up and 30 seconds per representative view is a starting fixture, not a universal duration. Readiness includes required assets and shaders. Do not disable required physics/effects in final measurements.

Report median and tail frame times, stalls and a defined frame budget. Refresh-capped FPS does not measure unused GPU headroom. Fixed-camera and traversal tests answer different questions. Phone viewport emulation on a desktop GPU is not phone hardware evidence.

Use A/B/B/A, preferably repeated, with one change and equivalent conditions. The helper's consistent-gain classification requires every adjacent pair to clear an explicit tolerance plus a quality pass. It is a conservative heuristic, not statistical significance. Retain failed and inconclusive runs rather than retrying until a lucky result appears.

Report targeted cost, change, conditions, before/after, visual impact, uncertainty and remaining failures. See [WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices); verify installed APIs and available extensions.
