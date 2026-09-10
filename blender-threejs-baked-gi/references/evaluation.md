# Evaluation and tested boundary

Run commands from the skill directory. Select a Python with NumPy installed;
Blender's bundled Python is sufficient. The tests generate small temporary
fixtures and leave production sources untouched.

```sh
"$GI_PYTHON" -m unittest discover -s scripts -p 'test_*.py' -v
"$GI_BLENDER" --background --factory-startup --python-exit-code 1 \
  --python scripts/blender_calibration.py -- --output-dir /tmp/gi-calibration-new
python "$SKILL_CREATOR/scripts/quick_validate.py" .
```

The output directory must not exist. The Blender command writes raw test EXRs,
two small editable fixture files and `results.json`; earlier outputs are never
replaced. No GPU or browser is used. Examples of the binaries used for the
recorded run are `/Applications/Blender.app/Contents/MacOS/Blender` and
`/Applications/Blender.app/Contents/Resources/5.1/python/bin/python3.13`.
Those paths are host-specific examples, not dependencies of the skill.
The optional skill-package validator uses PyYAML; the numerical helpers require
only NumPy (plus Blender for EXR/calibration), with no validator dependency.

Recorded on 2026-09-10 with Blender 5.1.2, Python 3.13, CPU, four Cycles threads:

| Check | Result |
| --- | --- |
| NumPy synthetic and CLI tests | 18 passed, 0 failed |
| Unit white sky, color-disabled diffuse | RGB 1.0, 1.0, 1.0 |
| Same sky with colored receiver albedo | RGB 1.0, 1.0, 1.0 |
| Unit normal-incidence sun direct | RGB 0.318309575 each, approximately 1/pi |
| Isolated sun indirect-only | Exactly 0 |
| Red neighboring wall, sky indirect-only | Mean RGB 0.15613349, 0.01107545, 0.00368038 |
| EXR independent RGB/alpha round trip | Maximum error 0 in all four cases |
| Packed float-image save/reload | Maximum error 0 |
| Source buffer/render settings | Preserved/restored |
| Official skill validator | Passed |
| Local reference links / project-specific residue | All resolve / none found |

All bake fixtures are 32×32 pixels. Unit sky/sun use 64 samples, isolated indirect
16, and colored bounce 128. These are calibration sample counts, not prescribed
production settings. EXR inputs include RGB 0, .003, .125, .5, 1, 2, 8 and
independent alpha 0, .001, .125, .25, .5, .75, 1. Display settings vary between
Standard and AgX with nondefault exposure/gamma; reload tests cover Linear Rec.709
and Non-Color. EXR headers confirm 32-bit FLOAT R/G/B/A channels.
Full numeric results are retained in [evaluation-results.json](evaluation-results.json).

Synthetic tests cover same-chart noise reduction, preserved contacts and narrow
light strips, positive fireflies/pairs, smooth maxima, disconnected chart colors,
folded normals, physical distance, majority-black atlas noise, no NaNs, unchanged
AO/input/uncovered data, actual coverage in the CLI, output overwrite rejection,
UV channel/orientation, inverse-transpose and mirrored fallback normals, sparse guide chart IDs and
unsupported static-donor formats. Padding tests retain valid black pixels with
zero AO, avoid wraparound and preserve covered values. Encoding rejects clipping.

The helper implementation is tested; the runtime and probe references are
adapter recipes. Prior implementation experience informs their invariants, but
this skill package does not ship or test a complete application shader/loader,
KTX encoder, glTF UV transfer, global overlap auditor or selective-rebake engine.
The Blender 5.1 fixture emits deprecation notices for `use_nodes`; rerun/adapt
against future APIs. On the recorded host the restricted Blender launch failed
before script execution; a permitted isolated factory launch completed normally.

Before delivering an adapted application, additionally test actual receiver UV
orientation and gutters, shader compilation with material variations, both preset
switches, stale revisions, failed/late downloads, repeated disposal, shared texture
ownership, instanced-probe LOD compaction and final decoded maps. Compare fixed
cameras on desktop/mobile. Measure actual hardware/DPR with a warmup and paired
baseline/candidate order; low-resolution compile fixtures prove no frame-rate claim.
Do not promote an optimization solely because it reduces a source-level operation
count. Verify saved-source reload and matching geometry/map/probe hashes last.
