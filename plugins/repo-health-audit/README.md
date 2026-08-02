# repo-health-audit

A recurring, full-repository health check across four lenses — security, UX, performance, DB — that files GitHub issues only for what actually matters (P0/P1) and opens auto-fix PRs for the mechanical ones.

Built to be portable: it never imposes its own branch/commit/PR workflow. `run-audit` reads whatever the target repo's own `CLAUDE.md`/`AGENTS.md` already says about branching, commit style, and PR conventions, and falls back to a safe default only when the repo has nothing documented.

This is deliberately **not** a replacement for Claude Code's built-in `/code-review` or `/security-review` — those are diff-scoped (they review a change). This plugin scans the whole codebase, on a schedule, to catch what was never part of any reviewed diff in the first place.

## Skills

| Skill | Role |
|---|---|
| `security-audit` | Full-repo scan for auth/authz gaps, injection, hardcoded secrets, unsafe deserialization, missing input validation |
| `ux-audit` | Full-repo scan for broken core flows and blocking accessibility failures — deliberately ignores visual/style/taste nits |
| `perf-audit` | Full-repo scan for N+1 queries, unnecessary re-renders, bundle bloat, blocking hot-path operations |
| `db-audit` | Full-repo scan of schema/migrations/queries for unsafe migrations, missing indexes, integrity gaps |
| `run-audit` | Orchestrator: runs the four above, dedupes against already-tracked findings, files issues for new P0/P1 only, opens auto-fix PRs for mechanical fixes (capped per run), never merges |

Each `*-audit` skill only **reports** structured findings — it doesn't touch issues or PRs itself. `run-audit` is the one that turns a report into GitHub state, and it's also the one meant to be called from a schedule (e.g. a daily Routine/cron running `/repo-health-audit:run-audit`), though every skill here works fine invoked manually too.

## Severity model

All five skills share one rubric: `reference/severity-rubric.md`. Only P0 (critical: exploitable now, core flow fully broken, data-loss risk) and P1 (high: a concrete defect that will predictably cause a P0 outcome) ever become an issue. P2 and below are discarded on purpose — a daily full-repo scan that files every stylistic nit would drown out what actually matters within days.

## Conventions assumed

- The target repo has (or can tolerate the absence of) a `CLAUDE.md`/`AGENTS.md` describing its own git workflow. If it has one, `run-audit` follows it exactly; if not, it falls back to a plain branch-and-PR default.
- Dedup across daily runs relies on a hidden fingerprint marker (`<!-- audit-fingerprint: ... -->`) embedded in each filed issue's body, and an `automated-audit` label used to find them again. Don't strip either manually, or the next run may re-file something already tracked.
- Scheduling itself (the daily cadence) is outside this plugin's scope — set up a Routine/cron per installed repo that calls `run-audit` on whatever interval you want.

## Origin

Grew out of a need to run the same "boring but important" health check across multiple personal repos without re-deciding, each time, what counts as worth an issue — the P0/P1-only filter and the fingerprint-based dedup exist specifically so this can run unattended every day without flooding the issue tracker.
