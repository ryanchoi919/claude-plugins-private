---
name: run-audit
description: Orchestrates security-audit/ux-audit/perf-audit/db-audit, keeps only P0/P1 findings, dedupes against already-tracked findings, files GitHub issues, and opens auto-fix PRs for the mechanical ones — while always deferring to the target repo's own branch/commit/PR rules. Meant to be run on a recurring schedule (e.g. daily via a Routine/cron calling this skill), but works fine invoked manually too. Triggers on requests like "오늘의 레포 점검 돌려줘", "run-audit 실행", "일일 코드 헬스체크".
---

# Run Audit

The orchestrator for this plugin. Runs all four lenses, then turns only the findings worth a human's attention into tracked GitHub issues, and fixes the ones it can fix safely and mechanically.

## When invoked

### 1. Learn the target repo's own rules first

Read the target repo's `CLAUDE.md`/`AGENTS.md` (or equivalent) if present. Extract: branch naming convention, commit message format/language, whether a worktree is required before editing, which branch is protected, PR title convention (e.g. Conventional Commits), and merge method. **This plugin always defers to what the repo already documents — it never imposes its own git workflow on top.** If the repo has none of this documented, fall back to a safe default: a dedicated branch off the default branch, a normal PR, no force-push, no auto-merge.

### 2. Run the four lenses

Invoke `security-audit`, `ux-audit`, `perf-audit`, and `db-audit` (in parallel via subagents if the environment supports it, sequentially otherwise). Each returns a list of P0/P1 findings only (they already discarded P2/P3 themselves — see each skill's own rubric application). Collect all of them.

If all four come back empty, stop here and report "no P0/P1 findings today" — that is a good outcome, not a failure to find something.

### 3. Dedupe against already-tracked findings

Before creating anything, search open issues labeled `automated-audit` (`gh issue list --label automated-audit --state open`, or the GitHub API equivalent). Each such issue's body carries a hidden fingerprint marker:

```
<!-- audit-fingerprint: <lens>:<short-rule-slug>:<file>:<line> -->
```

For every new finding, compute the same fingerprint shape and skip creating an issue if a matching one is already open. This is what keeps a daily run from re-filing the same thing every day. If a previously-fingerprinted issue is now closed and the same finding is detected again, treat it as new (something regressed) and file it again.

### 4. Label and file issues

For each finding that survives dedup:
- Labels: `automated-audit`, `severity:p0` or `severity:p1`, and one lens label (`security` / `ux` / `perf` / `db`). Reuse the repo's existing labels if equivalents already exist (e.g. it already has a `security` label) — only create the labels that don't exist yet. Never invent labels beyond this fixed set.
- Body: use the repo's own issue template if one exists (match its structure); otherwise use the finding's own fields (title/file/line/evidence/why_it_matters/suggested_fix) as the body. Always include the hidden fingerprint marker from step 3 so future runs can dedupe against it.
- Title: short and specific, not a restatement of the severity or lens.

### 5. Attempt fixes — mechanical only

For each newly-filed (or still-open, previously-filed) P0/P1 issue, decide: is this fix mechanical and low-risk (e.g. add a missing auth check mirroring a sibling endpoint, parameterize a concatenated query, add a missing index, add a null check)? Or does it require product/design judgment, or touch something high-blast-radius (a data migration affecting real rows, a core auth flow's behavior)?

- **Mechanical + low-risk:** implement the fix following the repo's own conventions (step 1), run whatever local verification the repo defines (lint/typecheck/test/build scripts — discover from `package.json`/CI config, don't assume a stack), commit, push, and open a PR that `Closes #<issue>` and follows the repo's PR title/template convention.
- **Everything else:** leave the issue open with a comment explaining why no PR was opened (what judgment call or risk it needs) — do not force a fix just to have one.

Never merge a PR yourself. Never force-push. Never bypass the repo's protected-branch rules to land a fix faster.

### 6. Respect the daily fix cap

Open at most 3 auto-fix PRs per run (configurable if the invoking context specifies a different number). If more mechanical fixes were eligible than the cap allows, say so explicitly in the run's summary ("N eligible, capped at 3, remaining M left as issues only") — never silently drop the rest.

### 7. Report

End with a short summary: findings per lens (including the P2/P3 discard count from each), how many were new vs. already-tracked, how many issues were filed, how many PRs opened vs. left issue-only, and why for the issue-only ones.

## Rules

- Never create an issue for a P2/P3 finding — the four lens skills already filter, but re-check before filing rather than trusting blindly.
- Never open a PR without a corresponding issue for it to close.
- If the target repo's own docs are ambiguous or contradictory about its git workflow, ask rather than guessing — an automated run picking the wrong branch/merge convention is worse than a delayed run.
- This skill is safe to invoke on a schedule with no human present; every irreversible action (merge, force-push, bypassing a protected branch) is out of scope for it regardless of how it's invoked.
