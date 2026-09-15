# Assembly architecture and mechanical modeling

## Resolve what is assembled

Start with personally inspected original images, the user's explanation and the [shared inventory/mockup workflow](../../blender-threejs-props/references/reference-modeling.md). Identify rigid modules, their supported groups, articulation/coupling links and visible components before detailed meshes. A single displayed vehicle can contain multiple articulated modules; several visible wheels can belong to one bogie. Joining objects into a collection does not define either relationship.

Record a compact assembly graph/table: module identity and purpose; local axes/pivot and scale; attached components; links to adjacent modules; intended motion; source/region and certainty. Label unknown hidden connections explicitly. Distinguish component counts from assembly counts and supported loads. Hidden architecture is not always inferable from photographs: use applicable domain knowledge or authoritative user clarification, and resolve consequential unknowns before committing dependent geometry or rigging. Keep that supplied context distinct from directly visible evidence.

For each moving/contact component identify purpose, attachments/load path, motion axis, meaningful states and actual mating/support surfaces. Use a simple cross-section or schematic where contact is ambiguous. A representation must preserve defining visible structure even when details are simplified. Repeated hardware needs per-photo visible minima, pair patterns and axle/part identity; hubs, tyres and brackets are not automatically separate wheels. Unknown hidden totals cannot justify contradicting visible minima.

When occluded-part ownership would change the assembly, state the competing interpretations explicitly and test them against the original. Compare projected component/axle directions, depth/occlusion order and stable landmarks: does the candidate follow a longitudinal sequence, a transverse counterpart or a different module? Use simple alternate mockups rendered at the source camera when the projection is difficult to reason through. Do not stop at naming alternatives if the existing evidence can discriminate between them. If ownership remains unresolved, retain the visible candidate and keep the dependent layout/count uncommitted; do not silently collapse it into the already modeled part.

## Build the modules and interfaces

Author components in named local coordinates with nominal dimensions and attachment anchors. Assemble from deliberate transforms; do not fit every finished component into an arbitrary bounding box. Keep rigid grouping and articulation separate from export/material batching. Test representative bends or hinge states when the architecture requires them, ensuring connected modules can occupy the proposed poses without disconnecting or interpenetrating.

Check enclosure relationships as an assembly: sides, rear and base must span or surround the intended contents as seen in the source. Individually clean end panels are insufficient if the overall wrap or support structure is missing. Distinguish a required structural extent from unseen manufacturing details.

For surfaces intended to meet, inspect actual boundary vertices/edges. Joining object containers does not weld topology. Choose a continuous shared boundary or a deliberate flush panel seam; remove exposed overlapping skins, accidental pockets and unmatched edges. Check edge flow/normals, preserving intentional creases without pinching or shading tears. Validate in close clay and side/grazing views, not only with a manifold test.

Preserve directly referenced silhouette before bevels and smoothing. A molded shell needs appropriate edge radii and controlled broad faces; large uniform fillets can make it look padded. Fix the underlying profile rather than masking a bad join with a rounded overlay. Spend polygons on curvature, thickness and recognizable construction before tiny fasteners. Good normals cannot repair missing volume.

## Function and human use

Establish intended use/contact and access/release states. Where human interaction matters, use documented estimated human/hand dimensions and realistic poses; retain clean views. Verify anatomy, support/contact and interpenetration. A named standing pose with a leg embedded in a seat cannot prove clearance.

Verify the intended contact pair and surface, rather than incidental contact nearby: a hand touching a control does not establish that its clamp or latch engages the target. Inspect critical interfaces in more than one view so projection overlap is not mistaken for contact or penetration.

Where clearance depends on movement, inspect relevant intermediate mechanism and user poses as well as endpoints. Two collision-free endpoints do not establish a clear transition. Check the actual load path, motion axis, body/hand reach, required free space and attachment continuity. Record hidden mechanism or motion-limit assumptions; do not claim full operation from a photographed display pose. Recheck affected states after pivot, angle, geometry or proxy changes.

## Review handoff

Use [shared evaluation](../../blender-threejs-props/references/evaluation.md) for the major-component correspondence table and separate visual reviewer. Include the assembly graph, directly observed counts, module/part distinctions, sources, selected poses and unresolved assumptions. A functional-role diagram or numeric contact equality does not prove the actual geometry, source fidelity or complete motion path. Lead with outstanding material discrepancies even if the latest local surface repair succeeded.
