# Evidence and rejected experiments

These observations motivated the skills; they are not universal tuning values.

The source project implemented resource sharing, instancing, material grouping, hysteretic LOD, static-shadow invalidation, packed-channel sampling reuse, compressed-geometry parity and cancellation/disposal. They establish mechanisms or specific byte/work reductions; their individual end-to-end FPS gains were not all isolated.

Smaller UASTC mobile lightmaps looked better than larger ETC1S maps with chroma blocks in neutral dark surfaces. Compare actual decoded output, not just source images.

A shader candidate moved seven lighting coefficient fetches into the vertex stage while retaining per-pixel normals. Four image comparisons were byte-identical, but A/B/B/A timings were inconsistent and worse in walking views. It was rejected.

A final 30-second desktop run at 1600×900 CSS and DPR 1.7 measured 42 FPS overview/39 walking despite about 95–138k main-pass triangles and 56–70 draws. It missed a 45 FPS target. Fresh GI-on/off runs were similarly slow and did not establish GI or JavaScript as the bottleneck. Older 60 FPS data under different load was not equivalent evidence.

Pixel 7 viewport emulation on the same Mac reached 60 FPS with lower DPR. That does not prove physical-phone performance. The source used Three.js 0.185.1; check target versions before adapting internals.

General lesson: preserve uncertainty and negative results. A source-level simplification, lower triangle count, smaller download or correct screenshot is not an unsupported speed claim.
