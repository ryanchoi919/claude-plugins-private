---
name: next-issue
description: Recommend which open GitHub issue to pick up next, by cross-referencing open issues against what's already claimed (open PRs, active local git worktrees) and any labeled priority/dependency signal, then optionally start a worktree for the chosen issue. Also answers "can I work on issue A and B in parallel?" by checking for overlap. Use when the user asks what to work on next, asks for a next-task recommendation, or asks whether two issues can be worked on at the same time.
---

# Next Issue

Recommends what to work on next from the repo's open issues, filtering out anything already in progress, and can kick off a worktree for the chosen issue.

## When invoked

1. **Gather signal:**
   - `gh issue list --state open` (labels, assignee, age) in the target repo.
   - `gh pr list --state open` — cross-reference PR bodies/branch names for linked issue numbers so those issues are known to be already in progress.
   - Local worktrees: check `.claude/worktrees/` (or `git worktree list`) for branch names already matching an issue number — these are also in progress even if no PR exists yet.
2. **Filter and rank.** Drop issues already covered by an open PR or active worktree. Among what's left, prefer (in rough order): explicit priority labels if the repo uses them, issues that block others (mentioned via "blocks #N" / "depends on #N" in issue bodies), then recency. Don't invent a priority scheme the repo doesn't have — if there's no signal beyond age, say so plainly instead of pretending to rank confidently.
3. **Present 2–4 candidates**, each with a one-line reason it's next (not just "it's open").
4. **Parallel-feasibility check** (when the user names specific issues, e.g. "323이랑 324 병행 가능해?"): read both issues' descriptions and, if they reference specific files/components, flag likely overlap or conflict risk. If there's not enough detail in either issue to judge, say that instead of guessing.
5. **Start work (only if asked).** If the user picks an issue to start now, derive a worktree name as `<type>-<issue#>-<slug>`, where `type` comes from the issue's label (bug→fix, enhancement/feature→feat, refactor→refactor, chore→chore, docs→docs; default to the label name itself if none of these match) and `slug` is a short kebab-case summary of the issue title. Confirm the name with the user, then create the worktree with that name.

## Rules

- Never create a worktree without the user explicitly choosing to start that issue in this turn — recommending and starting are separate steps.
- If neither PRs nor worktrees give any "already in progress" signal (e.g. a repo that doesn't use either convention), say the filter step found nothing to exclude rather than silently skipping it.
- Don't assume the naming convention (`<type>-<issue#>-<slug>`) applies to a repo where existing worktrees don't already follow it — check first.
