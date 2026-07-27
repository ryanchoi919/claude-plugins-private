---
name: doc-sync
description: Check whether a code change needs README/CHANGELOG/API-doc updates, and make them if so — reading the repo's existing docs first to match their structure and tone rather than imposing a fixed template. Use after committing (the doc-sync hook nudges this automatically), when the user asks to update/sync docs (e.g. "문서 갱신해줘", "README 업데이트해줘", "docs 동기화"), or before opening a PR.
---

# Doc Sync

Keeps README, CHANGELOG, and API docs from drifting behind the code they describe, without inventing doc structure a repo doesn't already have.

## When invoked

1. **Identify the change.** If triggered by the commit hook, use `git show HEAD` (or `git diff HEAD~1 HEAD`) for what was just committed. If invoked directly, use `git diff` / `git diff --staged`, or whatever range the user points at.
2. **Judge whether docs are actually affected.** Only these count:
   - Public API / interface / CLI flag / config schema changes -> API docs
   - User-facing feature/behavior changes, new setup steps -> README
   - Everything else (internal refactors, test-only changes, typo fixes) -> at most a one-line CHANGELOG entry, or nothing
   If nothing qualifies, say so in one line and stop — don't touch docs to justify having run.
3. **Read before writing.** Open the repo's actual README/CHANGELOG/docs first and match their existing structure, heading style, and changelog format (e.g. Keep a Changelog vs a plain bullet log) instead of imposing a different convention.
4. **Update precisely.** Touch only the sections the change actually affects — a new flag doesn't warrant rewriting an unrelated "Installation" section. If the repo has a doc-generation script (e.g. `npm run docs:build`, `typedoc`, `sphinx-build`), prefer running it over hand-editing generated output.
5. **Report, don't auto-commit.** Summarize what was updated and why (or why nothing was). Ask before committing the doc changes — whether to fold them into the existing commit (`git commit --amend`, only if unpushed) or as a separate commit is the user's call, not a default to assume.

## Rules

- Never commit doc changes without asking first, and never amend a commit that's already been pushed.
- If the repo has no README/CHANGELOG/docs at all, don't create one from scratch here — flag it and ask whether that's in scope, since that's a bigger decision than a doc-sync pass.
- This skill has no fixed template of its own; the repo's existing docs are the template.
