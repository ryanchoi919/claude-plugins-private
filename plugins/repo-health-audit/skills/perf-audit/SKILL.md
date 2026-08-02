---
name: perf-audit
description: Full-repository (not diff-scoped) performance audit — scans the whole codebase for N+1 queries, unnecessary re-renders, bundle bloat, and blocking hot-path operations, cross-checked against any existing perf budgets/gates the repo already has. Reports only P0/P1 findings per the shared severity rubric. Triggers on requests like "성능 관점에서 전체 점검해줘", "perf audit 돌려줘", "성능 이슈 전수 조사".
---

# Performance Audit

Scans the whole repository for performance defects with either a measured signal (an existing budget/gate this would blow past) or a clear reasoning chain to a user-visible symptom at realistic scale — not speculative micro-optimization.

## When invoked

1. **Read the severity rubric** at `${CLAUDE_PLUGIN_ROOT}/reference/severity-rubric.md`, especially the performance calibration note.
2. **Find existing perf gates/budgets first** (e.g. a bundle-size check script, a Lighthouse CI budget, a load-test threshold in CI config). Don't re-report what a gate already enforces and would already fail CI for — focus on what it doesn't cover.
3. **Scan systematically** for, at minimum:
   - N+1 query patterns: a loop issuing one DB/API call per iteration where a single batched call would do.
   - Missing memoization/unnecessary re-renders in hot UI paths (a component re-rendering a large list/tree on every keystroke or unrelated state change).
   - Bundle bloat: a heavy dependency imported in full where a subset or lighter alternative would do, especially in a client entry point.
   - Blocking operations on a hot path (synchronous I/O, unbounded synchronous loops, unindexed table scans) that would visibly degrade at realistic production scale/volume — reason about actual expected scale from the repo's domain docs, don't assume worst-case toy numbers.
4. **Classify.** A finding needs either a measured signal or a concrete "at realistic scale, this causes X (freeze/timeout/OOM)" chain to be P0/P1. Without either, it's P2 — discard.
5. **Report** P0/P1 findings only:
   ```
   - severity: P0|P1
     title: <short, specific>
     file: <path>
     line: <line or range>
     evidence: <the actual code showing the pattern>
     why_it_matters: <the measured signal, or the concrete scale-based reasoning chain>
     suggested_fix: <what would actually resolve it>
   ```
6. This skill only **reports** findings — it does not create issues or PRs itself.

## Rules

- "This could theoretically be faster" with no evidence it matters in practice is always P2 — discard it.
- Prefer citing an actual existing budget/gate the finding would blow past over inventing a performance target.
- Don't propose a rewrite/framework swap as the "suggested fix" for a single hot path — keep the suggested fix scoped to what a normal PR would actually do.
