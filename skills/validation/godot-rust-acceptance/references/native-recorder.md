# Bounded functional-run recorder

Use `scripts/record-run.mjs` with an existing Node runtime, a reviewed JSON
configuration and an explicitly authorized **new** output directory. It uses
only Node builtins. It executes one command without a shell or retries; it does
not fetch dependencies, build automatically or provide execution permission.
Obtain any host approval and coordinate source ownership before invoking it.

Invocation: `node /absolute/skill/scripts/record-run.mjs CONFIG.json NEW_OUTPUT_DIRECTORY`.
Paths containing spaces remain single command arguments.

## Configuration

All these fields are required unless marked optional:

| Field | Meaning |
| --- | --- |
| `cwd` | Existing absolute POSIX command working directory |
| `inputRoot` | Existing absolute directory containing the selected snapshot |
| `inputs` | Nonempty array of `{path, sha256}` records: unique relative paths, reviewed expected lowercase SHA-256 values |
| `command` | Nonempty argument array; first element is an absolute executable path |
| `wallLimitMs` | Finite limit within 1–60000 milliseconds |
| `expectedNativeExit` | Expected child exit code, integer 0–255 |
| `requiredStdout`, `requiredStderr` | Arrays of required nonempty literal strings |
| `forbiddenStdout`, `forbiddenStderr` | Arrays of forbidden nonempty literal strings |
| `stdoutEmpty` | Optional boolean asserting zero stdout bytes when true |

Include every relevant compiled source, manifest/lock, project configuration,
harness and prepared executable/library in the reviewed snapshot. The helper
does not discover a compiler's inputs. Expected hashes must come from the
accepted checkpoint, not merely hash whatever happens to be present. Symlinks
must resolve to regular files inside `inputRoot` and outside the output directory.
The configuration and helper are separately pinned in each run's receipts.

Configure identifying START and final PASS text for a positive harness, and
reject its explicit failure marker. For intentional negatives, configure the
actual native exit, intended diagnostic and absence of PASS; an unrelated
parser/import failure is not acceptance. At least one output assertion or
`stdoutEmpty: true` is required, but configuration alone does not make an
assertion meaningful. Game correctness still belongs to the real harness.

## Evidence and status

The output directory must not already exist. The helper retains `config.json`,
`expected.json` and actual `preflight.json` before a successful dependent child
launch. Failed preflight records refusal and does not launch the child.
`stdout.bin` and `stderr.bin` preserve complete raw bytes, including non-UTF8;
`result.json` records command, timing, native exit/signal/error, timeout latch,
input before/after, configuration/helper/receipt integrity, log hashes and
configured output assertions. Literal assertions decode logs as UTF-8; the
raw bytes and byte hashes are not replaced by that decoding.

Recorder exit 0 means the configured gate passed. Child exit 2 can therefore
have recorder exit 0 for a correctly asserted negative. Recorder exit 1 means
failed preflight or execution/evidence gate; exit 2 means invocation/configuration
refusal. Inspect `result.json` and original logs rather than infer the child's
status from the recorder's exit. An existing output directory is left untouched
and supplies no new result. There is no retry to overwrite prior failures.

The wall limit covers the child, not surrounding hashing/approval work. Only
the exact child created by this invocation is terminated on timeout. Descendant
process supervision is not provided; use the project's existing supervisor for
commands that need it. The helper verifies before/after checkpoints, not
adversarial immutability between them. Keep the team's reservation/private-copy
requirements and platform approval boundaries in force.

For coordinated timing, reuse the project's explicit START/END, all-owner SAFE,
hardware/load/thermal, strict unrounded maximum and immutable-artifact recorder.
This functional helper does not supply those performance gates.

When changing this helper, `scripts/test-record-run.mjs` runs six synthetic
controls in new macOS `/private/tmp` directories. It launches no Rust/Godot or
game benchmark and preserves its report/raw evidence rather than deleting it.
Those controls and independent forward usage validate recorder behavior, not
the game milestone.
