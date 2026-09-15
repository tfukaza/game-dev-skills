# Shared source-to-model workflow

## Describe the originals

Identify the target asset and source variant. Every author/reviewer, including delegated component agents, personally opens the relevant original images. Give delegated tasks those source files; inventories and generated/model images supplement rather than replace them. Record source-specific observations, not merely a list of opened filenames.

Before reference generation, describe observable features, repeated counts/arrangement, axes, proportions, material/shape boundaries and group relationships. Separate visible facts from inferred function or occluded construction; identify which photo/region supports each important observation. Do not silently combine conflicting variants or invent measurements.

Record visible minimum counts per photo/region and repeated pair patterns. Distinguish whole parts from concentric details, brackets and duplicate views of the same part; do not sum photos as additional components. Unknown hidden totals cannot excuse fewer parts than a source visibly shows. Resolve disputed counts with clearer original views, retaining specific uncertainty rather than labeling the entire assembly unknown. Record coverage and continuity too: two end panels do not necessarily reproduce an enclosing rear/side structure.

Name the plane/axis of important shapes. Image-space down may represent forward depth, not lower physical height; an apparent V in perspective is not evidence for a deep vertical V. Compare matched-perspective mockups plus orthographic views to resolve this. Explicit functional inferences, such as room for a hand, legs or a hidden mechanism, can constrain a plausible design without proving its hidden geometry.

When the defining shape depends on a progression (curvature, taper, thickness or slope), record its direction and where its extremes belong. For a reference-driven vertical coaster loop, distinguish a broad lower pull-up from a tighter crown; a continuous curve can still tighten in the wrong places. Check the actual radius trend as well as the silhouette. If inclined entry/exit transitions are requested, verify tangent grades at the joins and distinguish a momentary horizontal valley tangent from an extended flat section.

Treat dimensions and defining shape as coupled constraints. Do not meet a footprint target by silently reversing the reference curvature trend or flattening a crown. Inspect an equal-scale profile first, identify the height/width tradeoff, and state which constraint needs to change before refining that candidate.

## Preserve game scale and module boundaries

Lock the intended tile footprint, miniature proportions, and separate reusable units before importing architectural detail from photographs. Reference photos establish useful construction cues; they do not require life-size stairs, gates, roofs or circulation that the game's art direction deliberately abstracts. Treat a station strip and its entrance/exit kiosk tiles as separate assets when the brief calls for fixed modular connections. Record omitted internal transitions as intentional game abstractions instead of claiming fully modeled pedestrian access. Check the prop in the complete receiving scene early, including existing overhead track, before investing in detailed hardware.

## Build a simple proportion mockup

Use original observations and labeled inferences to build a neutral structural/proportion study before detailed modeling. Record controlling ratios or estimated dimensions, including thickness, major masses, spacing and clearances. Compare matching photo views and exact orthographic views before bevels, hardware or textures. Correct flattened volumes, oversized parts and missing structure. This study does not require a completed generated reference set first.

For human-used props, use a suitably scaled human/hand proxy when helpful; record estimated dimensions and pose. Inspect anatomy, posture, intended support/contact and interpenetration, not just bounding-box fit. Preserve usable reach and limb space, and retain a clean object view so the proxy does not conceal evidence. A generated proxy is not proof of ergonomic correctness. Use the [mechanical workflow](../../blender-mechanical-props/references/assembly-modeling.md) for functional interfaces and movement-critical states.

## Generate missing reference angles

If the source set is already adequate, do not regenerate it. Otherwise generate **one angle per image**, defaulting to exact orthographic front/side/back/top under flat diffuse neutral illumination. Secondary three-quarter views or close-ups answer construction questions; they do not replace required orthographic views.

Supply the actual mockup render at the requested angle as structure/camera/scale/occlusion anchor, plus the same original photographs as appearance/construction authority. Previously checked generated angles are secondary consistency inputs. Prompts or labels claiming an angle are not substitutes for the actual render. Preserve feature counts, relative scale, axes and source identity; do not force all known components to be visible through natural occlusion.

Inspect actual generated pixels for parallelism, expected occlusion and cross-view correspondence. Transverse identical components overlap in exact side projection; upright faces should not appear fully frontal in a top view. Check consistent counts, forward axes, landmarks, volumes and interfaces. Generated hidden views remain hypotheses. Reject mislabeled pseudo-orthographic views, contradictory construction or impossible proportions. Assemble a multi-view sheet only from accepted individual images.

Each new generated image is **PENDING** until a brief actual-image review records **PASS** or **REJECTED**, covering camera/occlusion, counts, axes and relevant interfaces. Pending/rejected images cannot drive later generation or modeling. A limited pass names its allowed use and excludes unresolved regions/hardware. Defer dependent detailed work while critical views remain unresolved; continue source-grounded mockup/interface studies that resolve the uncertainty.

## Iterate and review

Cross-reference the original inventory/photos, actual mockup and accepted generated views. A generated refinement cannot overwrite observed facts or silently change an interface. If original evidence or clearance checks require a mockup change, render fresh anchors and re-review affected references.

Spend geometry on recognizable contour, thickness and construction; place shallow grain/weave in materials. Low polygon count does not justify omitted defining components or blocky forms. Smooth shading cannot repair a wrong silhouette. For connected inorganic shells and controlled bevels use [mechanical props](../../blender-mechanical-props/SKILL.md); for fitted artwork use [UV textures](../../blender-uv-textures/SKILL.md).

Finish one prototype through the requested stages before multiplying the kit. Substantial creation/polish requires the [independent review](evaluation.md): an original-feature/model/status table covers every major component even during focused cleanup. Carry known deviations and missing evidence prominently into reports/handoffs. Keep original/generated images, prompts, observations, editable meshes and canonical artwork with the authoring source.
