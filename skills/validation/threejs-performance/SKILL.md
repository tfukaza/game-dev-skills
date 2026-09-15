---
name: threejs-performance
description: Diagnose and optimize interactive Three.js scenes with controlled CPU, GPU, loading, and memory measurements. Use for low frame rate, stutters, expensive scene assets, or growing resources; ordinary page navigation and Core Web Vitals belong to general web-performance guidance.
---

# Three.js performance

Find the limiting subsystem, change the responsible work, and measure the delivered result while preserving the user's quality constraints. JavaScript, triangle count, draw count and download size are not diagnoses on their own.

## Select the relevant module

- Start with [profiling and budgets](references/profiling.md).
- For application updates, submission, geometry or visibility: [CPU and geometry](references/cpu-geometry.md).
- For pixel cost, materials, transparency, lighting or effects: [GPU materials and lighting](references/gpu-materials.md).
- For first-use hitches, downloads, decode/upload and growth: [loading and memory](references/loading-memory.md).
- For executable tools: [helper contracts](references/tools.md). [Project evidence](references/evidence.md) separates mechanisms from rejected experiments; [evaluations](references/evaluation.md) record what was exercised.

## Optimize through evidence

1. Record scene/code/assets, camera or deterministic route, viewport and drawing-buffer dimensions, device/browser, readiness and warm-up. Preserve the project's budget.
2. Separate loading and first use from steady-state frames. Trace CPU activity and use asynchronous GPU timing where supported. Time around renderer.render() is not GPU time.
3. Choose one plausible bottleneck and one intervention. Keep a reversible baseline. Inspect installed Three.js code before adapting version-coupled internals.
4. Run equivalent serial A/B tests with alternating order. Verify image and gameplay requirements. Inconsistent results are inconclusive; fewer operations alone do not prove higher FPS.
5. Check representative views and lifecycle behavior. Record tradeoffs, unsupported measurements and unmet targets.

Do not silently reduce resolution, remove effects, change the comparison camera or reduce requested detail to make tests pass. Adaptive quality is an explicit product policy with bounds, hysteresis and recorded benchmark settings.

Use [asset delivery](../../pipeline/blender-threejs-asset-pipeline/SKILL.md) for source/export correctness and ownership, [GI](../../pipeline/blender-threejs-baked-gi/SKILL.md) for baking, and [scene QA](../threejs-scene-qa/SKILL.md) for visual acceptance.
