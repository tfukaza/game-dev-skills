---
name: godot-rust-acceptance
description: Verify Godot games backed by a Rust GDExtension using real command and input harnesses, deterministic snapshots, bounded large-map checks, and inspected render evidence. Use for acceptance runs, smoke-test creation, or debugging misleading or stalled Godot test runs; not for ordinary simulation implementation or art polish.
---

# Godot/Rust acceptance

Produce attributable evidence from the actual simulation, bridge and scene. A UI mock, ordinary game launch, parser exit or uninspected screenshot is not acceptance. This workflow comes from first-party Godot/Rust failures and verified corrections; no external implementation is incorporated.

## Route to the relevant workflow

- Read [harness and input](references/harness-input.md) when creating or debugging a Godot harness, watchdog, viewport or synthetic input path.
- Read [transaction coverage](references/transaction-coverage.md) when defining functional scenarios and authoritative before/after observations.
- Read [visual and performance evidence](references/visual-performance.md) for large maps, LOD convergence, render inspection and coordinated timing.
- Read [evidence and handoff](references/evidence-handoff.md) when preserving results, reporting failures or transferring an accepted run.
- Use the bundled [native recorder](references/native-recorder.md) when a new bounded command needs before/after input-integrity checks and complete raw output. Reuse a project recorder when it already supplies the required evidence.

## Establish the tested snapshot

Read the target repository's agent rules, pinned versions, acceptance criteria and current command runbook. Reuse its real harnesses. Build the adapter after Rust changes and import when scripts or extensions require it. Use the configured toolchain rather than an assumed shell path.

In a shared checkout, coordinate a compilable checkpoint and protect the relevant snapshot with the team's ownership mechanism. An intermediate non-exhaustive Rust match is an owner handoff problem, not a failed behavioral assertion. Do not patch another owner's source silently or hold broad reservations for ordinary build outputs.

Treat preflight as an awaited prerequisite. Start the dependent command only after it succeeds. Declare intentional derived-configuration differences before checking. A later correction can explain a failed preflight but cannot retroactively turn that run into a clean one.

For a complete Rust compiler-input closure, include first-party `include!`, `include_str!`, `include_bytes!`, build-script and generated-input references as well as `.rs` files. Resolve them against the declaring file and distinguish test-only fixtures from production inputs. This does not authorize reading or fetching third-party implementations.

Approval waits are not execution. Release shared source reservations before waiting for host approval, then reacquire and revalidate the complete snapshot before running. Release reservations promptly after the run. Never claim evidence for sources that changed during the approval gap.

## Keep evidence types separate

Functional, visual and performance claims require different observations. A deterministic JSON result does not prove geometry, a screenshot does not prove a transaction, and a bounded scheduler does not prove that all work finished. Persist actual command inputs, native status, complete raw output and meaningful before/after state. Inspect captures when making visual claims.

Require the project's independent review for material gates. Record exact commands, tested snapshot, assertions, exit status, inspected captures and remaining gaps in the established runbook or artifact. If a sandbox blocks a required scoped check, use the host approval mechanism; do not bypass permissions or classify an environment warning as a gameplay defect without evidence.
