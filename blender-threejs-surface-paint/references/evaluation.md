# Executed example checks and behavioral evaluation

Executed 2026-09-10 with Python 3.9.6 and Pillow 11.3.0, without NumPy, Blender, GPU work or AI image generation. Run from this skill directory:

```sh
python3 scripts/test_context_masks.py
python3 scripts/context_masks.py fixtures/wall.json /tmp/wall-mask.png --size 256
python3 scripts/context_masks.py fixtures/ground.json /tmp/ground-mask.png --size 256
python3 scripts/fixture_refresh.py /tmp/paint-refresh-example
```

All six tests passed (7.047 s for the first expanded run): contact-profile motion, quiet upper walls, varying ground density/traffic, default byte preservation, explicit reset backup, seeded output and coherent property-blend endpoints. The new regression uses a fresh 7.6×4.2 m wall, raises its four-point profile by .31 m, moves a drain, and retains all 154 edited RGBA pixels while unedited pixels exactly match freshly generated context. A second refresh keeps those edits and captures a 155th. The refreshed preview matches the active composite. Missing/modified baselines, changed world extents and unsupported context fields are rejected without replacing the active mask. Temporary test outputs are removed.

A later complete run passed in 3.491 s. A separate CLI smoke exercised initialization, `--refresh-context` and `--reset-manual`, checking exact zero-alpha manual values and the reset backup. Skill frontmatter validation also passed.

The actual generated images were inspected:

- [Wall illustration](../fixtures/wall-mask-preview.png): sloped contact-following fragmented wear, local drain runoff, restrained pigment difference and quiet upper wall.
- [Ground illustration](../fixtures/ground-mask-preview.png): wall-origin branches, variable interior density and a clearer central path.
- [Context-refresh comparison](../fixtures/context-refresh/comparison.png): active pigment and grime channels before/after moving the slope and drain. All 154 manual repair pixels remain exact; the runnable fixture retains baseline, manual values/coverage, both JSON inputs and [result](../fixtures/context-refresh/result.json).

Raw RGBA examples are `wall-mask.png` and `ground-mask.png`; alpha is grime data, not preview transparency. The saved context-refresh fixture runs at 128 px and uses a .28 m rise with a drain moved from [5.8,2.9] to [3.7,2.4]. Its active mask SHA256 is `ce96cc5cb2ad444a97b0dc88508dc85af4458edb5b1a72326cd2269c7f1e3fe2`.

These flat illustrations establish reproducibility, contextual distribution and preservation behavior. They do not claim final 3D material quality, real tangent-normal baking, projector alignment, atlas packing or physically simulated weathering. The preview shows pigment effects, not a full PBR response. Production appearance must be evaluated on actual geometry using matching material layers and exported texture tiers. Default preservation leaves the preview unchanged; explicit context refresh updates it. The override model is whole-pixel replacement at fixed registration, not channel-isolated strokes, reprojection or brush-history recovery.

## Independent fresh-input check

An independent reviewer exercised the documented CLI on a new 6.4×3.5 m wall, seed 78519, a different four-point slope and outlet. The first refresh retained 171 edited pixels; a second retained those plus 50 new edits (221 exact), including an explicitly erased all-zero pixel whose separate override coverage remained 255. Measured runoff centroids tracked anchors x=4.95→2.95→1.17 m within .005 m. Changed extents, unknown context and a modified generated baseline failed without changing active bytes. The reviewer opened the contact sheet and found the moved context and retained repairs coherent. No failures were found within the documented scope; no Blender, GPU or production files were used. This check was performed in an external isolated review workspace, not bundled as another duplicate fixture.

## Independent behavioral tasks

1. Give the agent a sloped plaster wall, drain and paved path. Require broad layered age that remains visible after all local decals are removed, plus a few semantically placed marks. Move the drain/ground profile and inspect the response without repainting unrelated regions.
2. Give the agent one manual mask edit and ask for a geometry-only source refresh. Confirm the edit survives and cached projector placements are invalidated when geometry changes. For final placement, a slab underside is not a valid ground hit.
3. Ask for exact multilingual painted lettering beside a mounted sign. Require correct spelling/shaping, appropriate representation for each, opaque painted surfaces, retained editable source and a delivered-file inspection. Do not accept illegible AI-generated lettering or a blanket ban on all decals/letter geometry.
