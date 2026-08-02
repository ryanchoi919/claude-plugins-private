---
name: db-audit
description: Full-repository (not diff-scoped) database audit — scans schema, migrations, and query code for missing indexes, unsafe/destructive migrations, and integrity constraint gaps. Reports only P0/P1 findings per the shared severity rubric. Triggers on requests like "DB 관점에서 전체 점검해줘", "db audit 돌려줘", "마이그레이션·스키마 위험 요소 점검".
---

# DB Audit

Scans the whole schema/migration history and query layer for defects that risk data loss, corruption, or integrity gaps — not naming/normalization taste.

## When invoked

1. **Read the severity rubric** at `${CLAUDE_PLUGIN_ROOT}/reference/severity-rubric.md`, especially the DB calibration note.
2. **Locate the schema/migration source of truth** (e.g. a `migrations/` or `supabase/migrations/` directory, an ORM schema file) and any existing data-model doc (e.g. an IA/domain-model spec) describing intended invariants — use it to know what's *supposed* to be true so gaps are judged against actual intent, not assumption.
3. **Scan systematically** for, at minimum:
   - Destructive/irreversible migrations already in the codebase: dropping a column/table with no backfill or reversibility path; adding `NOT NULL` without a backfill step for existing rows; a migration that would lock a large table in a way inconsistent with the repo's stated scale.
   - Missing indexes on columns actually queried in hot paths (join keys, frequent `WHERE`/`ORDER BY` targets) — cross-check against the query layer, not just the schema in isolation.
   - Missing integrity constraints where the domain model doc implies uniqueness/foreign-key relationships that the schema doesn't actually enforce, allowing real corruption (orphaned rows, duplicate rows that should be unique).
   - Data-versioning gaps: if the repo has a persisted-data version/migration mechanism for client-side or app-level data (not just the DB schema), check that a persisted-shape change bumped the version and added a migration step, per that repo's own documented convention.
4. **Classify.** Irreversible/destructive operations and real corruption risk are P0/P1. Naming, normalization preference, and style are P2 — discard.
5. **Report** P0/P1 findings only:
   ```
   - severity: P0|P1
     title: <short, specific>
     file: <path>
     line: <line or range, or migration filename>
     evidence: <the actual schema/migration/query code>
     why_it_matters: <the concrete data-loss/corruption/integrity scenario>
     suggested_fix: <what would actually resolve it>
   ```
6. This skill only **reports** findings — it does not create issues or PRs itself.

## Rules

- Never suggest a fix that itself requires a risky migration (e.g. "just drop and recreate the column") without flagging that the fix needs the same care as the original defect.
- A migration that already ran successfully in production isn't automatically safe to "fix" retroactively — if a past migration is now flagged, the suggested fix should be a forward migration, not editing history.
- Don't file naming/style/normalization preferences — those are P2, always discarded.
