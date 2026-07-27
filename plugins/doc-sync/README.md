# doc-sync

A Claude Code plugin that keeps README/CHANGELOG/API docs from drifting behind the code, by nudging a doc-check right after a commit and doing the actual update through one skill.

There's no `PostCommit` hook event in Claude Code (a GitHub feature request for one was closed as not planned), so this plugin approximates it with a `PostToolUse` hook filtered to `Bash(git commit:*)` — the same pattern `gh-issue-flow`'s `merge-cleanup-reminder` hook uses for `gh pr merge`.

## Skills

| Skill | Role |
|---|---|
| `doc-sync` | Judges whether a change needs README/CHANGELOG/API-doc updates, reads the repo's existing docs to match their structure, updates only what's affected, and asks before committing |

## Hooks

| Hook | Fires on | Role |
|---|---|---|
| `commit-doc-check` | `PostToolUse` for `Bash(git commit:*)` | Adds context nudging Claude to run a doc-sync pass on what was just committed |

## Conventions assumed

- No repo-specific config file is required — `doc-sync` reads whatever docs the repo already has (README, CHANGELOG, docs/ generator) instead of expecting a fixed template.
- The hook only fires when Claude runs `git commit` directly via the `Bash` tool — a commit made outside that (a separate terminal, a GUI client, a different tool path) won't trigger it. Call the `doc-sync` skill directly in that case (e.g. "문서 갱신해줘").
- `doc-sync` never commits on its own initiative; doc updates are proposed and reported, with commit/amend left to the user.

## Origin

Grew out of a question about whether Claude Code had a built-in or marketplace plugin for automatic doc upkeep on every code change — it doesn't, so this plugin fills that gap using the same hook + skill split as `gh-issue-flow`.
