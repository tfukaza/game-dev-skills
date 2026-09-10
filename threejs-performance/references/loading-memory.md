# Loading, decoding, uploading, and memory

Download completion, parsing, upload and first useful frame are different milestones. Keep an accurate lightweight fallback, then stage collision, surfaces and nearby props around intended interaction.

- Deduplicate requests and resources by stable identity, not display name. Count external textures, decoders, probes and every actually loaded preset/detail tier.
- Evaluate geometry compression against parity, decode time and decoder bytes. Smaller GLBs may have identical decoded vertex buffers.
- Evaluate KTX2 using the actual transcoded GPU format. File bytes, CPU decoded bytes and GPU residency differ. PNG/JPEG compression does not usually describe GPU storage. Include mips, layers, cube faces and render-target attachments.
- Choose resolution and packing by use. Color and non-color data require correct encodings; alpha may be independent data. Avoid unique full atlases for every instance.
- Bound decoder workers and upload batches. Parallel work can compete with frames or exceed memory. Stage shader preparation; measure first turns toward new materials as well as initial loading.
- Select tiers from explicit requirements and capabilities. Viewport emulation is not hardware detection. Adaptive settings require bounds, hysteresis and recorded state.
- Define resource ownership. Aborted requests may leave decoders running; release late results and forbid binding after disposal. Test remount after renderer caches warm. Dispose-call counts are not exact GPU-residency proof.
- Keep shared loaders alive while consumers need them. Close owned ImageBitmaps and revoke owned object URLs.

See [KTX2Loader](https://threejs.org/docs/pages/KTX2Loader.html) for capability detection and worker limits; use [asset delivery](../../blender-threejs-asset-pipeline/SKILL.md) for lifecycle correctness. Inventory estimates payload storage, not total driver memory.
