# gh-issue-flow

A Claude Code plugin covering the day-to-day GitHub issue/PR lifecycle on top of `gh` cli: file an issue from a rough description, pick the next one to work on, and merge a finished PR.

It doesn't replace `gh` — every skill is a set of instructions for Claude to drive `gh` cli well (checking for duplicates, matching a repo's own labels/templates, respecting whatever "in progress" already looks like) instead of running commands ad hoc each time.

## Skills

| Skill | Role |
|---|---|
| `create-issue` | Turns a rough bug report / idea / pasted log into a properly titled, structured, labeled GitHub issue — after checking for likely duplicates |
| `next-issue` | Recommends what to work on next by filtering open issues against what's already claimed (open PRs, active worktrees); can also judge whether two issues are safe to work on in parallel; starts a worktree for the chosen issue on request |
| `merge-pr` | Waits on CI for an open PR, merges once green (confirming merge method and, unless already authorized, the merge itself), then cleans up the branch and local worktree |

## Hooks

| Hook | Fires on | Role |
|---|---|---|
| `merge-cleanup-reminder` | `PostToolUse` for `Bash(gh pr merge:*)` | Reminds to check for a leftover local worktree/branch when a PR is merged directly via Bash instead of through the `merge-pr` skill |

## Conventions assumed

- Worktrees are named `<type>-<issue#>-<slug>` (e.g. `fix-118-sync-updatedat`, `feat-232-consistency-goal`), matching an existing convention rather than inventing a new one. `next-issue` checks a repo already follows this before relying on it.
- No repo-specific config file is required — each skill reads what the repo already has (issue templates, labels, branch protection/merge settings) instead of expecting a project-root doc like `VOICE.md` in the other plugins here. If that turns out to be too little context in practice, a shared config file is a natural follow-up.

## Origin

Grew out of three separate plugin ideas (issue creation, next-issue recommendation, PR merging) that all turned out to be stages of the same GitHub issue → work → PR lifecycle, so they ship as one plugin instead of three.
