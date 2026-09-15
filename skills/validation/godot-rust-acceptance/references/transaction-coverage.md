# Transaction coverage

Exercise the real public preview and apply API plus at least one real input gesture. Derive expectations from controlled scenarios and repository contracts; do not reimplement terrain, pricing, snapping, routing or collision logic inside the harness.

- Pure preview and drag leave state, cash, IDs and revision unchanged.
- Accepted release changes the intended shape or paint, charges the exact quote and commits once; repeated release cannot commit again.
- Cancel and no-op have no state or cash effect. Include a zero-height click when supported.
- A valid but unaffordable candidate retains its positive quote and candidate shape, refuses explicitly, reports the current revision and leaves authoritative state unchanged.
- Invalid geometry or input remains distinct from insufficient money; do not fabricate a valid patch.
- Cover actual apply for every scoped tool rather than many previews and one mutation. Check independent paint channels and boundary footprints where relevant.
- Dirty output eventually reaches the renderer; stable IDs and expected bounds survive rebuilds.

Stable JSON checks help determinism, but diagnostic sums do not prove spatial equality. Use exact geometry queries or validated local patch checks. Time diagnostic, command, initial-build and drain phases separately when repeated full-map scans could dominate the scenario.

Persist actual command inputs, quote metadata, supplied IDs and numeric geometry with complete before/after observations. Serialize vectors and centerlines explicitly; generic JSON formatting may turn engine vectors into display strings. A quoted cost alone does not preserve the candidate. Do not invent absent IDs or reconstruct geometry, snapping or pricing in the reviewer.
