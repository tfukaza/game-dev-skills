# Layout evaluation

## Executed helper checks

On 2026-09-10, from this skill folder:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Result: **6 tests passed**, no skips. Tests are in [test_height_contact.py](../scripts/test_height_contact.py). The suite runs the CLI through temporary JSON files and removes those files. It needs only Python's standard library.

Observed compact fixture output for anchors `[[0,0],[2,1]]`, `flatEnds=true`, `maxStep=1`:

| Station | Height | Derivative | Unit normal |
| --- | --- | --- | --- |
| 0 | 0 | 0 | [0, 1, 0] |
| 1 | 0.5 | 0.75 | [-0.6, 0.8, 0] |
| 2 | 1 | 0 | [0, 1, 0] |

For the upward triangle `[[0,0,0],[0,0.4,4],[4,1.2,4]]`, point `[1,0.3,1]` reports gap `0`, `contact`; `[1,0.5,1]` reports gap `0.2`, `floating`. A downward-facing upper triangle is excluded. Separate fixtures detect burial and missing support. The CLI exits 0 for a valid profile, 1 for unsupported contact, and 2 for malformed input.

Other assertions cover finite-difference derivative agreement, continuous nonzero grade through a continuing slope, zero grade at flat junctions, no monotonic-segment overshoot, mandatory shared stations and maximum segment length. These are geometry-helper checks, not a player-collision or reference-fidelity certificate.

## Behavioral scenarios ready for forward testing

These scenarios have **not** been run as independent agent evaluations. Give the agent the stated input and score the resulting artifacts/evidence, not whether it repeats this document.

| Scenario | Expected behavior and observable pass condition |
| --- | --- |
| A map establishes a low tunnel and upper bridge; a perspective reference appears to flatten the floor. | Separate source authority, preserve the lower route, calibrate plausible dimensions, and inspect clay from overview and eye height. Actual controller traverses the exported route; no solid base plate fills the tunnel. |
| User moves and rotates a complete landmark after detail work, and removes a neighboring building. | Update the shared assembly transform and dependent doors, attachments, metadata and collision. Removed building stays absent. Compare nearby views and routes; no orphan trim or stale hardcoded fallback remains. |
| A sloped road joins a flat courtyard, with curbs, a sidewalk and one nonplanar transition quad. | Share a height/derivative function, sample shared boundaries, use explicit matching triangles and continuous curb phase. Numerical junction checks and final runtime closeups show seated, continuous surfaces. |
| Two landmark widths have the wrong ratio; the current screenshot can be made to look closer by changing camera FOV. | Diagnose camera versus dimension mismatch. Change the relevant dimensions when necessary; do not claim uniform scale fixes a ratio. State remaining calibration assumptions. |

General invariants are shared spatial contracts, physical clearance, consistent triangulation and evidence from actual routes. Particular map levels, opening widths, landmark positions and camera angles are project choices; this package intentionally supplies no default scene-specific layout constants.

## Packaging check

Python syntax and all relative links pass. The official validator returned **Skill is valid!** (exit 0) with the central validation dependency path:

```sh
python3 /path/to/skill-creator/scripts/quick_validate.py /path/to/blender-threejs-layout
```

Those absolute paths record this validation run, not runtime requirements. The helper needs only stdlib; the official validator separately needs PyYAML. YAML and helper checks do not certify visual results.
