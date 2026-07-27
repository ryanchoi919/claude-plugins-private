---
name: doc-sync
description: Check whether a code change needs doc updates — not just README/CHANGELOG/API docs, but whatever a repo's DOC_MAP.md says exists (architecture docs, ADRs, runbooks, schemas, ...) — and make them, reading the affected docs first to match their structure and tone rather than imposing a fixed template. Use after committing (the doc-sync hook nudges this automatically), when the user asks to update/sync docs (e.g. "문서 갱신해줘", "README 업데이트해줘", "docs 동기화"), or before opening a PR.
---

# Doc Sync

Keeps a repo's docs from drifting behind the code they describe, using a `DOC_MAP.md` index (see the `doc-map` skill) to know what docs exist and what each one covers, instead of assuming README/CHANGELOG/API docs are the only kinds worth checking.

## When invoked

1. **Identify the change.** If triggered by the commit hook, use `git show HEAD` (or `git diff HEAD~1 HEAD`) for what was just committed. If invoked directly, use `git diff` / `git diff --staged`, or whatever range the user points at.
2. **Consult the doc map.** Look for `DOC_MAP.md` (or `docs/DOC_MAP.md`).
   - If it exists, use it to find which documented area(s) the change touches — this can be README/CHANGELOG/API docs, but just as easily an architecture doc, an ADR, a runbook, a schema file, or anything else the map lists. Skip entries the map marks `historical` — those are point-in-time records, not living docs to keep in sync.
   - If it doesn't exist, run the `doc-map` skill first rather than guessing at the repo's doc structure from scratch. If building a map isn't wanted right now, fall back to a quick heuristic scan of README/CHANGELOG/docs — but say explicitly that this is best-effort and may miss doc types the repo keeps elsewhere.
3. **Judge whether an update is warranted**, per matched doc:
   - Public API / interface / CLI flag / config schema changes -> whatever doc the map assigns to that area
   - User-facing feature/behavior changes, new setup steps -> README (or whatever the map assigns)
   - Everything else (internal refactors, test-only changes, typo fixes) -> at most a one-line CHANGELOG entry, or nothing
   If nothing qualifies, say so in one line and stop — don't touch docs to justify having run.
4. **Read before writing.** Open each matched doc and match its existing structure, heading style, and changelog format (e.g. Keep a Changelog vs a plain bullet log) instead of imposing a different convention.
5. **Update precisely.** Touch only the sections the change actually affects — a new flag doesn't warrant rewriting an unrelated "Installation" section. If the repo has a doc-generation script (e.g. `npm run docs:build`, `typedoc`, `sphinx-build`), prefer running it over hand-editing generated output.
6. **Report, don't auto-commit.** Summarize what was updated and why (or why nothing was). Ask before committing the doc changes — whether to fold them into the existing commit (`git commit --amend`, only if unpushed) or as a separate commit is the user's call, not a default to assume.

## Rules

- Never commit doc changes without asking first, and never amend a commit that's already been pushed.
- If the repo has no docs at all (no README, no `docs/`, nothing), don't create one from scratch here — flag it and ask whether that's in scope, since that's a bigger decision than a doc-sync pass.
- This skill has no fixed template of its own; the repo's existing docs (via `DOC_MAP.md`) are the template.
