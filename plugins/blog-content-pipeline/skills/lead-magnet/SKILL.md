---
name: lead-magnet
description: Step 9 of the content pipeline — draft the actual content for this post's lead magnet (grounded in the finished draft) and, if the project has a render script configured, produce the file. Use right after draft-write, before thumbnail-copy. Skip entirely if the constitution's Growth Mechanics section defines no lead-magnet pattern.
---

# Lead Magnet

Ninth step of the content pipeline, and an **approval gate**. Turns the lead-magnet *concept* `idea-refine` proposed into the actual content the reader will receive, grounded in the finished draft — not the idea-stage guess.

## When this applies

Requires `CONSTITUTION.md`'s **Growth Mechanics** section to have a filled-in **Lead magnet pattern** line — not missing, not "none yet", not the raw template placeholder. If it's missing or says there's no lead magnet for this project, **skip this step entirely** (report the skip in one line and move straight to `thumbnail-copy`) — most projects using this plugin have no lead magnet, and this step must cost them nothing.

## Steps

1. Re-read the Lead magnet pattern line. It should name: what kind of asset this is (e.g. "one-page PDF cheat sheet"), where its per-post content data lives (e.g. a data file path/filename convention), and — optionally — a render command to produce the actual file (e.g. a script path). Don't assume a shape beyond what that line actually says; different projects using this plugin may describe a different asset type (a PDF, a checklist image, a Notion template link) with a different data shape.
2. Using the just-finished draft as the primary source (not the `idea-refine`-stage concept, which was only ever a placeholder for "something like this will exist"), draft the actual content: for a phrase-sheet-style lead magnet, pull the actual phrases/etiquette notes/etc. that appear in the finished post rather than inventing new ones — the sheet's job is to be a portable, printable version of what the reader already just read, not a second independent piece of writing.
3. Write that content into the data file path/format the constitution's Lead magnet pattern line specifies, matching whatever schema that project has already established (check an existing sibling post's data file for the schema if one exists; don't invent a new shape for this post alone).
4. Report the drafted content to the user and **wait for explicit approval**. Do not proceed until approved — if they ask for changes, revise and re-present.
5. If the constitution's Lead magnet pattern line names a render command, run it now against the just-approved data file to produce the actual asset. If it names no render command, hand the approved content off to the user (for manual production, e.g. a designer) instead of blocking the pipeline on it — same fallback shape `image-generate` already uses when no generation backend is configured.
6. If the render command fails, don't retry in a loop or silently continue — report the failure once and ask the user how they want to proceed (fix and retry, or fall back to the manual handoff in step 5). Unlike a missing illustration, a lead magnet a post's CTA already promises the reader is a broken link if it never gets produced, so don't treat this failure as cosmetic.
