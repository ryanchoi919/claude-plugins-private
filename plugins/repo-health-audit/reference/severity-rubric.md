# Severity Rubric

Shared by every skill in this plugin (`security-audit`, `ux-audit`, `perf-audit`, `db-audit`, `run-audit`) so a finding gets the same severity regardless of which lens caught it. Read this before classifying anything.

Only **P0** and **P1** ever become a GitHub issue. **P2 and P3 are discarded** — do not create issues, backlog items, or tracking comments for them. This is a deliberate noise-control decision, not an oversight: a daily full-repo scan that files every stylistic nit would drown out the findings that actually matter within days.

## P0 — Critical

- Exploitable now, or actively causes data loss/corruption.
- A core user flow is completely broken (no workaround).
- A migration or schema change already in the codebase would corrupt or silently drop production data if applied as-is.

## P1 — High

- A clear, concrete defect that isn't (yet) being exploited or actively failing, but will predictably cause one of the P0 outcomes above under realistic conditions (e.g., an unauthenticated endpoint that leaks non-public data; an index-free query that will fall over at real production row counts; an accessibility failure that blocks an entire user group from a core flow, not a single edge case).
- Should be fixed soon, not urgently tonight.

## P2 and below — Discard

- Style, taste, "could be nicer," micro-optimizations with no measured or reasoned impact, minor copy inconsistencies, edge cases that require unusual input to hit.
- If you're unsure whether something is P1 or P2, default to P2 (discard). A missed P1 surfaces again next run; a wrongly-filed P2 is noise a human has to triage away.

## Lens-specific calibration

- **Security**: severity tracks exploitability and blast radius, not just "is this a known bad pattern." A hardcoded secret in a public repo is P0; the same pattern in a private repo with no external exposure is more likely P1.
- **UX**: only classify as P0/P1 when a user **cannot complete a core action** (checkout, sign-in, saving/syncing data, the product's primary loop) or an a11y failure locks out an entire assistive-tech user group from a core flow. Visual polish, copy tone, and "could be more delightful" are always P2 — discard, never file.
- **Performance**: needs either a measured signal (an existing budget/gate the finding would blow past) or a clear reasoning chain to a user-visible symptom (freeze, timeout, OOM) at realistic scale. "This could theoretically be O(n) instead of O(n^2)" with no evidence of it mattering in practice is P2.
- **DB**: irreversible/destructive schema or data operations are the P0/P1 zone (dropped columns without backfill, missing NOT NULL backfill, missing unique/foreign-key constraints that allow real corruption). Naming/style/normalization preferences are P2.
