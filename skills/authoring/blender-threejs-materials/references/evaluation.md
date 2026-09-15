# Executed checks and further behavioral evaluation

Executed 2026-09-10 with Node 24.12.0, Blender 5.1.2 and Python 3.9.6. Commands below are run from this skill directory; the recorded run used the same scripts through absolute staged paths. No application asset was modified.

## Numerical and Blender pair

```sh
node scripts/test_stochastic.mjs
node scripts/fixture_expected.mjs /tmp/stochastic-expected.json
blender --background --factory-startup --python-exit-code 1 --python scripts/fixture_blender.py -- --expected /tmp/stochastic-expected.json --report /tmp/stochastic-blender-parity.json
```

Use the installed Blender executable; the recorded macOS binary was `/Applications/Blender.app/Contents/MacOS/Blender`. Blender supplies NumPy; the host reference requires only Node. The fixture creates its own empty scene, uses CPU / 2 threads and does not save a blend or touch an open application. It writes only the requested report and temporary sibling JSONs beside the expected file.

Results:

- 726 two-sided probes across lattice edges/diagonals and positive/negative cells: maximum color/data/normal delta 1.99e-7 at2e-7 UV separation.
- 36 rotation/frequency/normal-basis cases: transformed slopes agree with finite differences of a known height field; maximum error 2.02e-11.
- Two real Blender node groups, three channels each,32 × 32 CPU EMIT bakes: maximum error 4.90e-7 against the JS reference. Nine image nodes reference three shared images; repeated calls reuse their group. Original UV layers/render selection remain intact.
- The fixture measures actual Cycles bake UV sample positions before comparing math. They differed from ideal centers by up to 0.0001502 UV; assuming exact centers initially caused a false normal mismatch. The final tolerance was not weakened to hide it.

Detailed graph results: [blender-parity.json](../fixtures/blender-parity.json). Constant image values isolate node arithmetic, rotations and frequency response; they do not establish image-filtering parity for spatial textures.

## Executed WebGL 2 shader fixture

Serve this skill directory with any local static server, then open `fixtures/stochastic-webgl.html`; for example:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

The page compiles and executes the included GLSL, reports `window.fixtureResult`, and releases its WebGL context after reading results. The recorded run used a short isolated Playwright browser with route-only file responses, no application server changes. It passed 18 cases: two presets × three normal conventions × three PBR outputs. Inputs are spatial sRGB color, spatial ORM and normals derived from an analytic height field. Bilinear repeat sampling and GPU sRGB decoding are compared to the JS reference. Maximum error was 0.0019631 in an RGBA8 framebuffer, approximately half an 8-bit step. Detailed result: [webgl-parity.json](../fixtures/webgl-parity.json).

This is shader-unit conformance, not a Three material integration or performance test. It does not test distant mip selection, anisotropy, mirrored object transforms, full BRDF rendering or resource lifecycle in a destination application. Use the sibling scene-QA/performance helpers for those checks. Blender's filtering remains renderer controlled.

## Independent behavioral tasks

1. Apply the skill to two adjoining floor meshes, a perpendicular wall and a roof with no unique paint map. Keep the supplied physical texture scale and existing unique UVs. Assess source/runtime normal direction and continuity while moving across region joins.
2. Give the agent an aged material with noisy lighting or codec damage plus intentional grain. Require isolated diagnostic views and a correction to the responsible layer without removing desired surface detail. Keep lighting/exposure fixed while comparing material changes.
3. Supply structured paving whose broad joints ghost under stochastic blending. Require a judged choice among constrained regions, less blending, a different base texture or no stochastic sampling; the agent should not force the included preset onto unsuitable material structure.
