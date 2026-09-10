# Static GLB auditor

`scripts/glb_audit.py` is a read-only stdlib helper. It is a small verifier, not an exporter, decoder or universal glTF validator.

## Supported boundary

- glTF 2 binary with one embedded buffer and named, unique nodes; one node instance per mesh.
- Triangle primitives, indexed or unindexed, with finite scalar/VEC2/VEC3/VEC4 accessors. Standard integer and float components, accessor offsets, strides and normalized integer attributes are supported.
- Static hierarchy/transform comparison, node and mesh metadata, primitive/material binding, all original vertex attributes, and declared added attributes.
- Optional global unique-UV audit of a chosen VEC2 channel: finite/in-range coordinates, noncollapsed physical triangles and exact positive-area overlap checks with a spatial broad phase. Shared chart edges are allowed.

It explicitly rejects animation, skinning, morph targets, mesh instancing, sparse accessors, external/multiple buffers, required extensions and geometry-compression extensions. POSITION and direction attributes must be floats. Every mesh must be instantiated once; scene roots must be valid, node extras objects, and transforms finite affine matrices or valid TRS. Decompress a copy with a trusted decoder before comparison; preserve and separately verify the packaged output. Embedded image bytes and material texture bindings are compared; external image contents and GPU decoding are **not** checked by this script.

The strict comparison allows vertex/index/triangle reordering, cyclic corner order and vertex splitting. Reversed winding, changed original attribute bits/types, lost channels, changed material assignment or changed metadata fail. Node names are identities. Node-array reordering is accepted when named hierarchy/scene membership stays the same; changed child order is treated as a contract change. Materials/images/textures/samplers must retain their JSON ordering and content.

An allowed added attribute is checked for structural validity but must be requested with `--uv` if it is intended to be a unique atlas. Tiled UV0 normally should **not** be checked for global uniqueness. Fixed numerical epsilons target ordinary metre-scale assets; extremely small/large geometry needs a reviewed tolerance policy, not a silent pass.

## Commands

From the skill folder:

```sh
python3 scripts/glb_audit.py inspect input.glb
python3 scripts/glb_audit.py inspect input.glb --uv TEXCOORD_2
python3 scripts/glb_audit.py compare source.glb candidate.glb
python3 scripts/glb_audit.py compare source.glb candidate.glb --allow-added TEXCOORD_2 --allow-extra-key lightingRevision --uv TEXCOORD_2
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

The helper prints JSON and never overwrites a GLB. Exit 0 means the requested checks passed; exit 1 means a valid comparison/atlas failed; exit 2 means unsupported or malformed input. Reports identify the input hashes, triangle/attribute counts, checked scope and failures. UV reports scan all triangles, count every overlap and retain at most 20 example pairs; `complete` describes scan completion, not success.

`--allow-extra-key` permits only those named **node extras** to be added or changed. It does not bypass layout transforms, material metadata or unrelated extras. Compare a corrected baseline only after separately documenting any intended geometry delta. Use [export contracts](export-contracts.md) for that distinction.
