# Encoding, codecs and budgets

Measure final covered linear RGB across all presets. Choose one declared range
R with headroom; a power of two with 20% headroom is a tested starting choice.
`choose_encoding_range` and `encode_rgb8` in `scripts/lightmap_io.py` preserve HDR
through `sRGB(L/R)` and reject clipping. AO alpha stays linear and independent.
For the calibrated E/pi bake, decoded RGB needs R*pi to supply irradiance.
An unnecessarily high fixed R wastes dark-region precision. Do not choose R
from a low-sample pilot when final transport can have a higher maximum.

Compare the actual decoded codec candidate with the same uncompressed values
under identical color-space, orientation, min/mag filters and mip policy. In
particular, a loader may give an uncompressed data texture nearest filtering
while a compressed texture uses linear mip filtering. Normalize sampling before
blaming block compression. Inspect dim neutral walls, colored bounce, contacts
and grazing ground; overall image averages can hide visible chroma blocks.

ETC1S can be efficient but produced colored patches in dim lighting in a tested
scene; raising its quality did not cure that region. UASTC with Zstd preserved
neutrality better. This is evidence for a comparison, not a universal codec ban.
A lower-resolution UASTC tier can beat higher-resolution ETC1S perceptually.
Explicit tent-filtered mip chains avoided ringing in that workflow. Test RDO,
quality and alternative filters on the actual content before choosing defaults.

Configure the installed KTX tool from its current `--help`: source transfer is
sRGB for encoded RGB, alpha independent, orientation explicitly chosen, full
mips, desired codec/quality and lossless container compression. This skill does
not bundle a platform-specific encoder or assert one CLI version works everywhere.
Record tool version, source/output hashes, resolution, channels, mips and codec.

Budget the complete tier: geometry, shared textures, decoder payload, both
lighting presets and probes, plus GPU allocation where relevant. Optional contact
AO alpha may be omitted if the runtime declares the change and preserves RGB
lighting; do not silently lower resolution or switch codecs after a budget failure.
Present measured options and inspect their visible tradeoffs. Encoded hashes
participate in lighting revision because compression changes transported radiance
used by later captures. Keep source EXRs; neither JPEG nor display-tonemapped
images are an appropriate intermediate for lighting transport.
