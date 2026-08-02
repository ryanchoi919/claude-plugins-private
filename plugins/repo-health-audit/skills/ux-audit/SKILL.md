---
name: ux-audit
description: Full-repository UX audit — scans the whole product surface (not a diff) for broken core flows and blocking accessibility failures, deliberately ignoring visual/style/taste nits. Reports only P0/P1 findings per the shared severity rubric. Triggers on requests like "UX 관점에서 전체 점검해줘", "ux audit 돌려줘", "핵심 플로우 끊긴 곳 있는지 점검".
---

# UX Audit

Scans the whole UI/product surface for defects that stop a user from completing something, not for design taste. This lens is the easiest of the four to over-report on, so the bar for what counts is deliberately narrow — see Rules.

## When invoked

1. **Read the severity rubric** at `${CLAUDE_PLUGIN_ROOT}/reference/severity-rubric.md`, especially the UX calibration note, before classifying anything.
2. **Identify the product's core loop(s)** first — the handful of actions the product exists to let a user do (e.g. sign in, complete checkout, save/sync data, the primary create/edit/complete action of the app). Read the repo's own product docs (PRD, IA/domain model doc, README) if present to confirm what actually counts as "core" here instead of guessing.
3. **Walk the code for each core flow**, looking for:
   - A step that can silently fail with no error state shown to the user (network/save failure swallowed, no retry/feedback).
   - A state the UI can reach with no way out (dead-end loading spinner, no error boundary, a form that can't be submitted or cancelled).
   - An accessibility failure that blocks an entire assistive-tech user group from a core flow (e.g. a core action reachable only via a mouse-only handler with no keyboard/ARIA equivalent; a modal that traps focus with no escape).
   - i18n breakage that blocks comprehension of a core flow (missing translation key rendering as raw key/undefined in a primary screen) — not minor phrasing inconsistencies.
4. **Classify strictly.** If it's arguably a matter of taste, polish, or an edge case requiring unusual input, it's P2 — discard it, don't include it in the report.
5. **Report** P0/P1 findings only, same structured format as the other audit skills:
   ```
   - severity: P0|P1
     title: <short, specific>
     file: <path>
     line: <line or range>
     evidence: <the actual code/markup showing the break>
     why_it_matters: <which core flow breaks, and for whom>
     suggested_fix: <what would actually resolve it>
   ```
6. This skill only **reports** findings — it does not create issues or PRs itself.

## Rules

- Default to discarding when in doubt. This lens exists to catch things that stop a user cold, not to run a design review.
- Never file: color/spacing/copy-tone preferences, "could be more delightful," minor inconsistency between two screens that doesn't block anything, missing-but-non-critical loading skeletons.
- If the repo has no discoverable definition of its "core flow," ask rather than guessing broadly — a wrong core-flow assumption makes every subsequent finding wrong too.
