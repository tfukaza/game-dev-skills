# Stylized presentation materials

Use this reference when a game concept needs a deliberate painterly or miniature presentation rather than strict physical realism.

## Establish palette and lighting separately

Record a scene-specific hierarchy: background value, lit versus shaded neutrals, saturated focal colors and dark structural anchors. Keep environmental illumination separate from the camera background. Establish a directional sun and readable cast shadows before adding broad fill. A finite softbox below tall geometry can make a diorama gloomy and uneven; inspect the whole vertical envelope and place area fill above it when appropriate. A restrained opposing directional fill and sky ambient can keep shaded faces readable without creating competing hard shadows.

Compare one representative material per family through identical camera views before propagating changes. Brighter ambient light can wash paint into pastel, while brighter foliage pigment can become uniformly fluorescent. Evaluate light/fill balance and base color together rather than increasing global exposure. Record the chosen palette in the asset's art-direction notes instead of turning it into a universal default.

Review broad painted variation at the intended game-camera distance and close up. Small patches repeated across every surface can still read as noisy mottling. Enlarge the distribution or reduce contrast while retaining quiet areas. Preserve editable controls for tint, contrast, scale and roughness.

## Stylized water and submerged effects

Editable blue or turquoise surface color, reduced transmission and softened reflections are valid when they improve game-camera readability. Retain selected depth, ripple, jet and impact cues rather than treating physically exact water nodes as the quality criterion.

Constrain caustic color and emission to submerged receiving surfaces. A basin-floor material may also be assigned to a wall above the waterline, so inspect polygon coverage rather than trusting names. Use water-height masks or distinct dry materials; with surface waves, follow local water height or fade below its minimum. Keep dry coping and exterior masonry clean unless reflected light is part of the brief.

Match caustic contrast and coverage to the reference hierarchy. Making an effect visible does not justify a uniformly bright network. For subdued water, break up the pattern spatially and let jets, impact ripples and the water surface remain primary. Review a low oblique angle as well as the game camera.

## Review preservation

For a material-only pass, compare saved geometry, UVs, polygon material assignments, packed-image contents and cutout links with the source. A plausible render alone does not prove preservation. Give an independent reviewer the original art-direction reference and actual renders, and distinguish material/lighting findings from frozen geometry outside the pass.
