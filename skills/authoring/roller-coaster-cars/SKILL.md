---
name: roller-coaster-cars
description: Model and review roller coaster car/train game assets from a specific reference family, resolving articulated lead and seating modules, bogies, wheel-to-rail relationships, passenger enclosure and restraint states. Use for coaster vehicles, not whole-park layout or track-element design.
---

# Roller coaster cars

Resolve the target car architecture before dependent geometry or rigging. A display assembly can combine a lead/nose unit with a separate seating unit; visible components, rigid modules and bogie sets are not interchangeable counts. Hidden articulation may require domain knowledge or user clarification rather than photo inference.

Read [the car workflow](references/car-workflow.md). Apply [mechanical props](../blender-mechanical-props/SKILL.md) for assembly graphs, connected shells, pivots, hardware and motion, and the shared [source/mockup workflow](../blender-threejs-props/references/reference-modeling.md) for direct photo inspection and generated reference acceptance.

For the user-clarified four-across display reference that motivated this skill, the assembly is a lead unit plus a seating unit, articulated together, with one bogie set per unit. This is authoritative supplied domain context, not a structure a generic observer is expected to discover from those photographs. Preserve it for that target; it is **not** a rule for all coaster families or a wheel-count specification. Establish each target's module graph from applicable domain context, user explanation and visible evidence; audit visible wheel minima separately.

Use actual source-grounded mockup renders to anchor generated angles. Keep original photos authoritative, particularly new wheel or coupling close-ups; generated hardware and prior scoped passes cannot settle missing source facts. Check the whole seating enclosure and articulation, not only the nose, four seats and isolated side fins.

Inspect seated restraint contact, raised access and relevant intermediate poses with a documented human proxy. When resizing vehicles, keep the proxy outside the vehicle scale hierarchy and verify its standing-equivalent stature from body segment lengths. Repose full-size limbs to test the footwell; do not shrink the proxy with the car or narrow it merely to make the fit pass. Document proxy shoulder/hip widths and distinguish a fit pose from a complete motion sweep. Separate inferred mechanism/motion limits from observations. After geometry acceptance, use [Blender UV textures](../blender-uv-textures/SKILL.md) for the actual unwrap/export/generate/reapply workflow.

Before substantial creation/polish is complete, a separate critical reviewer must use [shared evaluation](../blender-threejs-props/references/evaluation.md), directly inspecting originals and actual multi-angle renders. The correspondence must cover modules, bogies/wheels, couplings, enclosure, seats, restraints and passenger space. Report all material mismatches prominently even during focused surface cleanup.
