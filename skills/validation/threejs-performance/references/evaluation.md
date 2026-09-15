# Executed performance-helper evaluation

Recorded 2026-09-10 with Node 24.12.0.

From this skill directory:

```sh
node --test scripts/test-performance.mjs
```

Seven tests pass: per-frame distribution/stalls, ABBA gain/regression/inconclusive outcomes, incomparable resolution changes, failed visual acceptance, restoration on failures, RAF cancellation, post-final-quality cancellation, mip/block/cube/MSAA payload accounting, deduplication and explicit unknown GPU formats.

An independent evaluator used unfamiliar synthetic optimization proposals and profiles. It classified inconsistent paired timings as inconclusive, a lower-resolution candidate as incomparable, a failed-appearance candidate as rejected, and a consistent 20% synthetic change as a candidate requiring real-device validation. CPU-update, pixel-cost and first-exposure traces were routed to different investigations.

The evaluator found a cancellation hole after the final async quality callback. It was fixed and independently retested. Scene-QA review also fixed final-capture cancellation, immutable historical snapshots and cleanup settlement after disposal failures. Regression cases are permanent in the owning test suites.

These are helper and reasoning checks, not a performance claim about the current game or target devices. The tiny browser scene fixture in the QA skill exercises real RAF capture but uses a screenshot-friendly drawing buffer and a short sample, so it is not a production benchmark.

For replayable synthetic inputs see [performance cases](../fixtures/performance-input.json). They are explicitly synthetic; do not relabel them as traces captured from real hardware.
