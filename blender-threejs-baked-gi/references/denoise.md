# Lighting-only guarded filtering

Use `scripts/denoise_lightmaps.py` on finite linear H×W×4 floats, before encoding.
RGB is diffuse lighting; alpha is copied exactly. Do not use albedo, material
normal maps or a display screenshot as guides. Preserve immutable raw passes.

The reusable API separates expensive guide construction from filtering presets:

```python
guides = rasterize_guides(donor, size, uv_channel=2, flip_v=True)
guides['coverage'] &= raw_bake_coverage
filtered = denoise_with_guides(rgba, guides)
```

Guide keys: `position` and unit `normal` H×W×3; integer `chart_id`, positive
`texel_size` and boolean `coverage` H×W. Position and texel size use the same world
units. Row orientation must match the lighting. Chart IDs may be sparse; the
filter compacts them without mutating the source guides. Invalid/uncovered
pixels remain unchanged. Do not infer coverage from combined AO alpha.

The rasterizer supports square atlases and audited static glTF 2 GLBs: one
embedded uncompressed buffer, triangle primitives, indexed or nonindexed
geometry, ordinary node transforms and a selected atlas UV channel. It rejects
required extensions and optional node/mesh/primitive/accessor/buffer-view
extensions, external/multiple buffers, mesh compression, animation,
skinning, morphs, GPU instancing, sparse accessors, singular transforms and
out-of-bounds data. Triangle index accessors must be unsigned SCALAR data.
Missing normals derive from the local face orientation and transform correctly
through reflected nodes. It is not a complete glTF validator or global overlap auditor.
Use NPZ guides from an independently audited rasterizer for unsupported formats
or rectangular atlases. `world_tolerance`/`uv_tolerance` control chart edge
matching; defaults 1e-5 world units and 1e-7 UV units assume meter-scale geometry.

The tested default filter first removes isolated **positive** RGB outliers using
eight same-chart, nearby, normal-compatible neighbors. It requires six neighbors,
uses median/MAD with relative and absolute floors, and retains samples supported
by nearby bright structure. Then nine-tap bilateral passes at steps 1, 2, 4 use
fixed corrected luminance, per-chart noise estimates, normal and world-distance
guards. Black/black pairs do not determine illuminated-chart noise. Thresholds
are empirical defaults, not a guaranteed estimator for every transport solution;
inspect narrow light features and mean-energy change on representative charts.

CLI, with a NumPy-equipped Python:

```sh
python scripts/denoise_lightmaps.py raw.npy filtered.npy \
  --donor donor.glb --coverage raw-coverage.npy --uv-channel 2 \
  --save-guides used-guides.npz
python scripts/denoise_lightmaps.py second-raw.npy second-filtered.npy \
  --guides used-guides.npz --coverage second-coverage.npy
```

Outputs must be new paths. `--keep-gltf-v` disables the default reflection;
`--no-firefly` and `--noise-sigma` support controlled diagnostics. Raw NPY/EXR,
coverage and NPZ guides must belong to the same geometry/atlas generation.
Reusing guides after geometry repair without verifying their identity is unsafe.
Padding remains a separate step after filtering. NumPy row chunks bound temporary
filter memory; rasterizing large atlases still requires several full guide arrays.
