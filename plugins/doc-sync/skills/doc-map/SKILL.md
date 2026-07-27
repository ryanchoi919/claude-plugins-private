---
name: doc-map
description: Build or update a documentation index (DOC_MAP.md) cataloguing a repo's actual guide/reference docs — README, CHANGELOG, docs/ guides, ADRs, policies, API/schema specs, runbooks — filtered by content (not just path) to exclude point-in-time records and agent/session scratch state. Use before a doc-sync pass on a repo that has no map yet, when repo structure has changed significantly, or when the user asks to "문서 지도 만들어줘" / "doc map 갱신해줘".
---

# Doc Map

Produces or updates `DOC_MAP.md` — a table mapping each real doc artifact in the repo to what it covers — so `doc-sync` (or a human) can tell which docs are affected by a change without rediscovering the repo's doc structure, or sifting scratch state, from scratch every time.

## When invoked

1. **Inventory candidates broadly, but skip obvious noise directories first.** Look for `README*`, `CHANGELOG*`, `CONTRIBUTING*`, everything under `docs/**`, ADRs (`docs/adr/**`, `**/ADR*`), API/schema specs (OpenAPI, GraphQL SDL, `.proto`), runbooks, onboarding guides, and any other `**/*.md` — but exclude `node_modules`/`vendor`/build output, nested `worktrees/` (duplicate copies of the repo), `coverage/` (generated reports), and agent/session-scratch directories (e.g. `.agents/`). A useful signal for the latter: if the same filenames (`handoff.md`, `progress.md`, `BRIEFING.md`, and the like) repeat across many sibling directories, that's per-run scratch state, not documentation — exclude the whole directory rather than judging each file individually.
2. **Classify each remaining candidate by content, not just location** — real repos mix genuine guides in with other markdown even outside any scratch directory (e.g. a repo root can hold both an `AGENTS.md` style guide and a one-off `ORIGINAL_REQUEST.md` or a milestone status note side by side). Skim enough of each file to sort it into:
   - **Guide/reference** — describes ongoing, current state: setup/usage guides, policies, architecture/design docs, specs, contracts, schemas, changelogs, ADRs. Tone is typically prescriptive/descriptive of "how this works" or "how to do X", not narrating a specific past event. → include in the map as something `doc-sync` should keep current.
   - **Point-in-time record** — a snapshot of a specific past decision, request, plan, or status (a milestone plan, an original feature request, a "ready for release" checkpoint). Often narrates a specific moment, references a fixed date/milestone name, or reads like a one-off deliverable rather than a living reference. → may still be worth listing (context is useful), but mark it clearly as historical so `doc-sync` doesn't try to keep it "in sync" with ongoing code changes.
   - **Scratch/working state** — belongs to a specific agent run, session log, or personal draft never meant as a lasting reference. → exclude entirely, don't list even as historical.
   When a file is ambiguous, err toward asking rather than silently guessing — especially for anything that reads like policy (legal/compliance/security) where miscategorizing could matter.
3. **Write/update `DOC_MAP.md`** at the repo root (or `docs/DOC_MAP.md` if the repo already keeps its docs under `docs/`), as a table: `Doc | Covers | Type | Notes` (`Type` is `guide`/`spec`/`policy`/`changelog`/`historical`, etc.).
   - Keep existing entries whose target file still exists and still looks accurate.
   - Add new entries for anything not yet listed.
   - Flag — don't silently delete — entries whose target file no longer exists.
4. **Report** what was added, updated, or flagged as stale, and roughly how many candidates were excluded as scratch state (so the exclusion isn't silent).

## Rules

- Never delete a doc file to "resolve" a stale map entry — flagging it is the extent of this skill's scope.
- If the repo already has an equivalent index (e.g. a `docs/README.md` that lists all docs), extend/align with that instead of creating a second, competing index.
- One line per entry — this is a map, not a summary of each document's full contents.
- If inventory turns up an unusually large number of matches (hundreds), that volume is itself a signal most of them are scratch state or duplicated worktree content — pause and say so instead of trying to classify all of them individually.
