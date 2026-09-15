# Game Dev Skills

Reusable agent skills for game-development work across Blender, Three.js,
Godot and Rust. The guidance and helpers grew out of multiple first-party game
projects and preserve the practical lessons from modeling, asset delivery,
runtime diagnosis and acceptance testing.

Each skill is a self-contained directory with a `SKILL.md` entrypoint and any
supporting `references/`, `scripts/`, `fixtures/` or `agents/` metadata it needs.
Install or copy the complete directory for the skill you want. Skills can be
used individually; workflows that link to related skills expect those sibling
packages to be installed too.

## Authoring

| Skill | Use it for |
| --- | --- |
| [`blender-threejs-layout`](skills/authoring/blender-threejs-layout/) | Terrain, topology, playable routes, object placement, clearance and grounded structural supports |
| [`blender-threejs-props`](skills/authoring/blender-threejs-props/) | Reference-driven props, source inventories, variants, foliage, graphics, stylized figures and placement contacts |
| [`blender-mechanical-props`](skills/authoring/blender-mechanical-props/) | Vehicles and inorganic assemblies with modules, pivots, joined shells, hardware, load paths and human interfaces |
| [`roller-coaster-cars`](skills/authoring/roller-coaster-cars/) | Coaster-specific lead and passenger modules, bogies, wheel-to-rail relationships, articulation, seats and restraints |
| [`blender-uv-textures`](skills/authoring/blender-uv-textures/) | Real mesh UV unwraps, checker inspection, exported layouts, generated fitted artwork and mapped-model verification |
| [`blender-threejs-materials`](skills/authoring/blender-threejs-materials/) | PBR response, physical texture scale, stochastic tiling, stylized palette/lighting and water-material treatment |
| [`blender-threejs-surface-paint`](skills/authoring/blender-threejs-surface-paint/) | Layered wear, deposits, repairs, markings, lettering and context-aware surface masks |

## Pipeline

| Skill | Use it for |
| --- | --- |
| [`blender-threejs-environments`](skills/pipeline/blender-threejs-environments/) | Coordinating substantial environment work across layout, art, delivery and runtime validation |
| [`blender-threejs-asset-pipeline`](skills/pipeline/blender-threejs-asset-pipeline/) | GLB export, source/runtime parity, attribute preservation, packaging, LOD contracts and resource ownership |
| [`blender-threejs-baked-gi`](skills/pipeline/blender-threejs-baked-gi/) | Calibrated Cycles baking, lightmap atlases, denoising, transport, compression and optional probes |

## Validation

| Skill | Use it for |
| --- | --- |
| [`threejs-performance`](skills/validation/threejs-performance/) | Controlled CPU, GPU, loading and memory measurement for interactive Three.js scenes |
| [`threejs-scene-qa`](skills/validation/threejs-scene-qa/) | Reference comparison, traversal, render-defect isolation, asset failures and resource lifecycle checks |
| [`godot-rust-acceptance`](skills/validation/godot-rust-acceptance/) | Bounded Godot/GDExtension harnesses, deterministic snapshots, transaction checks, inspected renders and native evidence |

## Routing overview

- Start with `blender-threejs-environments` for a whole environment; use the
  focused authoring or validation skill directly for an isolated task.
- General props route mechanical assemblies to `blender-mechanical-props`,
  coaster trains to `roller-coaster-cars`, and fitted artwork to
  `blender-uv-textures`.
- Asset delivery owns Blender-to-runtime preservation. Scene QA owns visible
  behavior and failures. Performance owns measured cost. Passing one does not
  imply the others passed.
- Godot/Rust acceptance is independent of the Three.js pipeline and uses the
  target project's real harnesses and contracts.

## Path migration

The skill names and `$skill-name` invocations are unchanged. Repository paths
changed in this reorganization:

| Previous path | Current path |
| --- | --- |
| `blender-threejs-layout/` | `skills/authoring/blender-threejs-layout/` |
| `blender-threejs-props/` | `skills/authoring/blender-threejs-props/` |
| `blender-threejs-materials/` | `skills/authoring/blender-threejs-materials/` |
| `blender-threejs-surface-paint/` | `skills/authoring/blender-threejs-surface-paint/` |
| `blender-threejs-environments/` | `skills/pipeline/blender-threejs-environments/` |
| `blender-threejs-asset-pipeline/` | `skills/pipeline/blender-threejs-asset-pipeline/` |
| `blender-threejs-baked-gi/` | `skills/pipeline/blender-threejs-baked-gi/` |
| `threejs-performance/` | `skills/validation/threejs-performance/` |
| `threejs-scene-qa/` | `skills/validation/threejs-scene-qa/` |

The mechanical-prop, roller-coaster, UV-texture and Godot/Rust acceptance
packages are new to this repository and have no previous public path.
