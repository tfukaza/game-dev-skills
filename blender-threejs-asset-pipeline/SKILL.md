---
name: blender-threejs-asset-pipeline
description: Export, package or update Blender assets for Three.js while preserving scene metadata, geometry, UVs, normals, tangents, material bindings and LOD contracts. Use for source/runtime parity, narrow asset repairs, delivery revisions and loading or disposal correctness.
---

Treat the editable source, export candidate and delivered runtime files as related artifacts with an explicit contract. Preserve the user's scene and existing authorization; use an isolated Blender process/copy for destructive preparation or export when the interactive source must remain available.

## Establish what must survive

Record units/axes, root transforms, semantic IDs, material bindings, required vertex attributes and the purpose of each UV channel. UV channel numbers are project contracts, not universal conventions. Preserve tangent handedness and authored normals when their materials depend on them. Collision, editable components, visible meshes and authoring helpers need explicit export membership.

Keep source editability separate from runtime grouping. Joining visible meshes by compatible material may be useful, but retain semantic aliases and the intended spatial granularity. Preserve prop pivots, identity and artwork across LODs; use [props](../blender-threejs-props/SKILL.md). For newly required bitmap artwork, prefer the available image-generation tool and retain its editable source; export optimization must not replace the requested artwork or introduce floating glyph meshes.

Read [export contracts](references/export-contracts.md) before pipeline changes, late geometry repairs or lifecycle work. Use [glb_audit.py](scripts/glb_audit.py) for its supported static, uncompressed GLB subset. It compares actual triangle-corner attributes despite vertex splitting/reordering, checks metadata/material bindings and optionally checks a unique UV atlas. Read [auditor usage and limits](references/glb-auditor.md) first; unsupported inputs fail explicitly rather than receiving a false preservation claim.

## Stage, verify and deliver

Export the intended collections only. Apply the declared triangulation consistently and verify transforms in the runtime coordinate system. Compare actual candidates, not just generator parameters. A successful exporter exit is not a parity or appearance check.

For an attribute-only update, require unchanged original geometry and attributes. For an intentional geometry repair, define the changed faces/regions, preserve unaffected attributes, and report the delta honestly. Carry interpolated UVs from each contributing triangle when clipping; do not assign charts by nearest position at seams or opposite-facing surfaces. Keep collision changes separate and intentional. See [layout](../blender-threejs-layout/SKILL.md) for route geometry and [baked GI](../blender-threejs-baked-gi/SKILL.md) when changed or newly exposed receivers need lighting updates.

Bind dependent assets to matching revisions and verify content hashes before promotion. Existing authorization permits routine staging and validation; internal checks do not introduce repeated user confirmations. Publish a coherent set of model, material/lighting manifest and dependent data, then exercise the actual delivered path. Keep a previous usable set or staged fallback when interrupted updates could leave incompatible artifacts.

Preserve resource ownership across streaming, shared materials and LODs. Cancellation can arrive after download, decode or parse; late results still require cleanup. Restore shader hooks and dispose only owned resources, exactly once. Verify partial failure and teardown/reopen, including external image requests. Read the lifecycle section in [export contracts](references/export-contracts.md).

Use [scene QA](../threejs-scene-qa/SKILL.md) for visual/interaction evidence and [performance](../threejs-performance/SKILL.md) for cost, budgets, compression tradeoffs and measurements. This skill owns correctness of the artifact transition, not a second performance inventory. [Evaluation](references/evaluation.md) records runnable helper tests and behavioral scenarios.
