---
name: doc-map
description: Build or update a documentation index (DOC_MAP.md) cataloguing every doc artifact in a repo — README, CHANGELOG, docs/ guides, ADRs, API/schema specs, runbooks, onboarding docs, wiki — and which code/feature area each one covers. Use before a doc-sync pass on a repo that has no map yet, when repo structure has changed significantly, or when the user asks to "문서 지도 만들어줘" / "doc map 갱신해줘".
---

# Doc Map

Produces or updates `DOC_MAP.md` — a table mapping each doc artifact in the repo to what it covers — so `doc-sync` (or a human) can tell which docs are affected by a change without rediscovering the repo's doc structure from scratch every time.

## When invoked

1. **Inventory doc artifacts broadly.** Don't stop at README/CHANGELOG. Look for: `README*`, `CHANGELOG*`, `CONTRIBUTING*`, everything under `docs/**`, ADRs (`docs/adr/**`, `**/ADR*`), API/schema specs (OpenAPI, GraphQL SDL, `.proto`), runbooks, onboarding guides, and any other `**/*.md` outside `node_modules`/`vendor`/build output. If the repo links to an external wiki, note it but don't try to crawl it.
2. **Summarize each artifact's scope in one line**, cross-referencing the codebase where it clarifies things (e.g. does `docs/api.md` correspond to `src/api/`?). Example lines: "README.md — setup, usage, CLI flags", "docs/architecture.md — system components and data flow", "docs/adr/0007-*.md — decision to adopt X".
3. **Write/update `DOC_MAP.md`** at the repo root (or `docs/DOC_MAP.md` if the repo already keeps its docs under `docs/`), as a table: `Doc | Covers | Notes`.
   - Keep existing entries whose target file still exists and still looks accurate.
   - Add new entries for anything not yet listed.
   - Flag — don't silently delete — entries whose target file no longer exists.
4. **Report** what was added, updated, or flagged as stale.

## Rules

- Never delete a doc file to "resolve" a stale map entry — flagging it is the extent of this skill's scope.
- If the repo already has an equivalent index (e.g. a `docs/README.md` that lists all docs), extend/align with that instead of creating a second, competing index.
- One line per entry — this is a map, not a summary of each document's full contents.
