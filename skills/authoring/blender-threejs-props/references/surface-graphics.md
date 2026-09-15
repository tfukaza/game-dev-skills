# Surface graphics and lettering

Default to image-generated, game-appropriate lettering/label artwork, following the user's preference. Do not silently replace it with Times, Menlo or another available system font because that is easier to rasterize. Existing user artwork and explicit typography directions take precedence.

1. Establish exact wording, capitalization, punctuation, reading direction and line breaks. Separate fixed identity (brand/logo) from variable fields (serial or unit markings).
2. Generate a canonical flat artwork image in the intended visual language. Keep perspective, generated highlights and cast shadows out of painted surface artwork.
3. Inspect the actual pixels at readable scale. OCR is a useful check, not proof. Correct a misspelling through a targeted revision that preserves the remaining design; prompt text alone does not prove correct rendered text.
4. Reuse this canonical design on all appropriate views/variants. Independently regenerating every side can invent new logos or wording. Keep intentionally different face layouts explicit.
5. Bake to the actual printable UV surface using a lighting-free color pass, or project a tightly conforming decal. Preserve substrate/roughness/normal response as appropriate. Define the intended print region: artwork may deliberately span ribs or battens, but must not leak onto unrelated fasteners, opposite faces or undersides.
6. Verify grazing-angle contact, barrel curvature, folds/corrugations, orientation and detail transitions. No floating glyphs, mirrored words, duplicate markings or z-fighting.

A PNG of lettering is a wordmark/label/glyph sheet, not a TTF/OTF with kerning, shaping and a usable alphabet. Building a reusable font is a separate task when requested. Deterministic typesetting can be appropriate for existing approved fonts, changing technical fields or a user-selected font, but is not a silent generic-font replacement for the chosen artwork workflow.

Retain artwork, prompts and hashes with the editable source. Mounted signs need physical supports; printed text usually does not need text-shaped geometry. Intentionally embossed/cast lettering is a different material and silhouette case.

Use the [surface-paint projection/bake guidance](../../blender-threejs-surface-paint/references/decals-lettering.md) for application mechanics.
