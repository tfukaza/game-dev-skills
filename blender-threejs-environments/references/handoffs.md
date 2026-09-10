# Scene contracts and handoffs

Use the project's existing schema rather than imposing a new engine API. This is a worksheet, not a mandatory file format.

| Contract | Minimum useful content |
|---|---|
| Reference | Source and relevant annotation; intended feature; measured vs inferred dimensions |
| Layout | Units, axes, origin; stable surface/assembly IDs; boundaries; elevation function and junction stations |
| View | Camera transform, projection, viewport; neighboring and walking views |
| Assets | Root/pivot, authored scale, materials, UV roles, contact anchors, collision source, detail levels |
| Paint | Receiver ID/revision, macro region, physical scale, source masks, protected hand edits |
| Lighting | Geometry/UV revisions, transport convention, presets, raw/filtered/encoded hashes |
| Delivery | Entry manifest, tier dependencies, decoder requirements, resource owners |
| Acceptance | Observable visual/traversal criteria, device/quality budgets, evidence location |

A handoff identifies changed contracts and downstream invalidation. Include the exact output revision and failed checks. Source-only work is not published work; successful export is not a visual pass.

A rotated building includes recesses, doors, shutters, fixtures, cables, signs, collision and paint anchors. A ground change regenerates shared boundary samples rather than independently nudging neighboring meshes.

Retain old sources until the replacement is verified. Prefer reproducible exports and immutable raw bakes; regeneration must not overwrite manually painted sources implicitly.
