# Reference-specific coaster car workflow

## Establish the family and assembly graph

Personally inspect the supplied originals, including new close-ups, before relying on a previous inventory. Identify source variants: front lead car, intermediate seating car, display assembly and rear train photo may show different modules or trim. Record which source supports each module, joint, wheel group and enclosing surface. Do not silently combine variants into an invented chassis.

Write the assembly graph before detailed meshes. Distinguish visual parts (hood, cheek, seat, wheel), rigid modules, bogie groups and articulation/coupling links. Define what "bogie set" means in this target rather than using the term alternately for one rail-side cluster and a complete supported unit. Record relative axes/pivots, support ownership and movement between modules.

**User-clarified motivating target:** a four-across display assembly contains a lead/nose unit and a seating unit, articulated together, with one bogie set supporting each unit. Treat this as authoritative supplied domain knowledge; these photographs do not make the hidden module division readily inferable to a generic observer. Once supplied, preserve that architecture rather than one rigid body with arbitrary fore/aft wheel clusters. The number of individual load/guide/upstop wheels within each bogie remains a separate source-audit question. For other targets, establish architecture from applicable domain knowledge, user clarification and visible evidence before committing dependent geometry or rigging; this example is not a universal template.

A new close-up of the nose and main running gear can invalidate an earlier count or structure interpretation. Re-audit its visible minima, repeated pairs and attachments rather than fitting it to the existing model. Do not bake exact wheel counts from a previous generated sheet or from an ambiguous photograph into a reusable assumption.

## Audit running gear per bogie and rail

For each identified module/bogie, record original photo/region, visible wheel minima, likely roles, repeated or tandem pattern, observed axes and specific occlusions. Distinguish separate tyres/wheels from hub rings, mounting brackets, shadows and far-side overlap. Do not add counts across different views of the same group. Uncertain complete totals do not justify omitting a clearly visible second part.

Where the selected family uses load, side-guide and upstop wheels, verify that those roles engage the **same intended rail tube** above, laterally and below. Use a transverse rail/wheel schematic and longitudinal arrangement before detailed hardware. A single example of each role can be functionally plausible yet wrong for the source's repeated arrangement. Set gauge, tube radius, wheel sizes and clearances from project dimensions or documented estimates; there are no universal dimensions in this skill.

Give axles, hubs, forks and supporting members a coherent load path to the correct module. Inspect actual rendered rail contacts from end, side and three-quarter views; numeric circle equations do not prove polygon contact or hidden attachment. Preserve module articulation and verify representative relative poses, rather than welding together every visible piece for convenience. Export/material batching must not erase this architecture.

## Seats, enclosure and restraint function

Count seating rows, seats per row and individual restraints from the relevant originals; account for real occlusion in each view. Preserve the seat-facing axis, cushion thickness, back recline and local mounting orientation. Spend geometry on rounded contact surfaces and the overall bucket silhouette before shallow seams or tiny bolts.

Treat rear, side and base fairings as an enclosing/supporting assembly. Check what spans the whole row and wraps around it, not just whether an end fin is present at either side. Record the source-defined panel coverage, continuity, mounting height and relationship to all seats. A tidy triangular panel can still be a major construction mismatch.

For lap-restraint targets, reason from function: a lowered pad meets the seated person's lap through a supported stem/pivot; a raised state permits access. Establish the pivot location, axis, load path and intended motion, labeling unobserved linkage and limits as inferred. Use a human proxy with documented estimated stature and pose. Inspect pad-to-lap contact itself, not merely hands reaching the pad; verify the stem between legs, usable knee/foot volume and platform support from side plus front/three-quarter views.

Inspect raised and relevant intermediate mechanism/user poses, checking that knees/shins clear the pan and the restraint clears body and hood. A standing proxy embedded in the seat cannot establish egress. Record the actual sampled states and remaining untested movement; endpoint success is not full continuous exit validation. Other restraint types need their corresponding function, not a forced lap-bar design.

## Shape, references and surfaces

Use the target's source description and simple mockup first. For the pointed fairing family studied here, distinguish forward nose projection in XY plan from frontal Z height: a perspective V is not a deep vertical bow. Use matched-photo perspective and true orthographic views. Preserve independently observed central hood, shoulder crease, lip and cheek volume; user art direction can streamline them, but should be labeled rather than presented as exact measurement.

Author deliberate shared shell boundaries or flush seams, not overlapping rounded primitives. Check the actual vertices/edges and clay render. Keep molded fairings taut with appropriate rim radii; avoid padded blobs and equally avoid reducing an enclosing shell to disconnected thin fins. Body cleanup must preserve passenger volume, source-defined assembly coverage and module interfaces. When tightening train spacing, measure the lead-to-first-passenger interface separately from repeated passenger-to-passenger gaps. Include rigid footwell trays and projecting rims in the body-clearance set; exclude only intentionally contacting mechanical joints, with those exclusions recorded. A clear seat surround does not prove the foot deck clears the nose. Enumerate every coupling from the assembly graph instead of relying on a case-sensitive name filter.

Generate missing views one at a time with actual mockup renders and originals, following [shared reference acceptance](../../blender-threejs-props/references/reference-modeling.md). Old generated wheel details are not authority. UV work follows the standalone [actual mesh workflow](../../blender-uv-textures/SKILL.md), after the architecture and surfaces are accepted.

## Required correspondence before signoff

Use the [shared review table](../../blender-threejs-props/references/evaluation.md) to cover at least the target's major groups: lead/nose module; seating module(s); articulation/couplings; bogie ownership and visible wheel minima; rear/side/base enclosure; seats and mountings; restraints and sampled states; passenger platform/clearance. Add UV/material evidence when that stage is in scope.

Each reviewer personally views the original evidence and records source-specific observations against actual model views. A low-poly brief does not authorize dropping defining modules, paired hardware or enclosure coverage. A local surface fix may pass while overall correspondence remains failed or incomplete; lead the report/handoff with those known deviations. Do not advance unresolved hardware or architecture as an accepted generation anchor.
