# doc-sync

A Claude Code plugin that keeps a repo's docs from drifting behind the code, by nudging a doc-check right after a commit and doing the actual update through a skill that consults a documentation map rather than assuming README/CHANGELOG/API docs are the only kinds that exist.

There's no `PostCommit` hook event in Claude Code (a GitHub feature request for one was closed as not planned), so this plugin approximates it with a `PostToolUse` hook filtered to `Bash(git commit:*)` — the same pattern `gh-issue-flow`'s `merge-cleanup-reminder` hook uses for `gh pr merge`.

## Skills

| Skill | Role |
|---|---|
| `doc-map` | Scans a repo for doc artifacts (README, CHANGELOG, docs/ guides, ADRs, schemas, runbooks, ...), classifies each by content as guide/reference, point-in-time record, or scratch state (not just by directory), and writes/updates `DOC_MAP.md` with what's left |
| `doc-sync` | Judges whether a change needs a doc update, consulting `DOC_MAP.md` (running `doc-map` first if it's missing) instead of a fixed doc-type list, reads the affected doc(s) to match their structure, updates only what's affected, and asks before committing |

## Hooks

| Hook | Fires on | Role |
|---|---|---|
| `commit-doc-check` | `PostToolUse` for `Bash(git commit:*)` | Adds context nudging Claude to run a doc-sync pass on what was just committed |

## Conventions assumed

- No repo-specific config file is required beyond `DOC_MAP.md` itself, which `doc-map` creates/maintains in the target repo (root, or `docs/` if that's already where the repo keeps its docs) — a persisted index instead of re-discovering doc structure from scratch on every run.
- `DOC_MAP.md` entries are filtered by content, not just path: only guide/reference-type docs (setup guides, policies, specs, changelogs, ADRs) are treated as things `doc-sync` should keep current. Point-in-time records (a specific past plan/request/status) may still be listed but marked `historical`, and `doc-sync` skips those. Agent/session scratch state (e.g. `.agents/`, per-run `handoff.md`/`progress.md` files) is excluded entirely, not just deprioritized.
- The hook only fires when Claude runs `git commit` directly via the `Bash` tool — a commit made outside that (a separate terminal, a GUI client, a different tool path) won't trigger it. Call the `doc-sync` skill directly in that case (e.g. "문서 갱신해줘").
- Neither skill commits on its own initiative; doc updates (and the map itself) are proposed and reported, with commit/amend left to the user.

## Origin

Grew out of a question about whether Claude Code had a built-in or marketplace plugin for automatic doc upkeep on every code change — it doesn't, so this plugin fills that gap using the same hook + skill split as `gh-issue-flow`. The `doc-map` skill was added after noticing the first cut of `doc-sync` hardcoded README/CHANGELOG/API as the only doc types worth checking, and re-scanned repo structure from scratch on every trigger instead of working off a stable index.

A local test against a real, actively-developed repo (579 markdown files) surfaced that path-based filtering alone isn't enough: 63 of those files were multi-agent orchestration scratch state (`.agents/**/handoff.md`, `progress.md`, `BRIEFING.md`) sitting alongside genuine guides, and the repo root itself mixed living guides (`AGENTS.md`, `CLAUDE.md`) with one-off, point-in-time records (`ORIGINAL_REQUEST.md`, a milestone status note) in the same directory. That's what motivated classifying candidates by content (guide/reference vs. point-in-time record vs. scratch) rather than relying on directory location alone.
