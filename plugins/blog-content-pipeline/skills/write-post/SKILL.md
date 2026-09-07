---
name: write-post
description: Master entry point for writing a new blog post — runs the full 10-step pipeline (trend research through SEO vetting) in order, pausing at approval gates, optionally preceded by `topic-scout` when no seed topic exists yet. Use when the user asks to write/plan a new post and hasn't specified a single narrower step.
---

# Write Post — Pipeline Control Tower

This is the entry point for producing one new post from a seed topic through to a publish-ready, vetted draft. It's a thin orchestrator: the actual work lives in the other skills in this plugin, invoked in a fixed order.

## Prerequisite

Before anything else, confirm `CONSTITUTION.md` exists at the project root. If it doesn't, stop and run the `constitution` skill first — every step below depends on it for voice, taxonomy, and formatting rules. Do not improvise brand/voice decisions yourself; they belong in the constitution, not in this pipeline.

## Step 0 (optional) — no seed topic yet?

If the user (or the scheduled run invoking this pipeline) hasn't given a seed topic, run `topic-scout` first. It scans the knowledge base and the web for candidates, dedupes against existing posts, and stops at its own approval gate for the human to pick one — this is what lets an unattended/scheduled run still find something worth writing about without skipping human sign-off on *what* gets written. Once a topic is picked (there or by the user directly), continue at step 1 below with that topic as the seed.

If a seed topic is already in hand, skip `topic-scout` entirely and start at step 1.

## Pipeline order

Run these in sequence. Steps 1-2 and 4 chain automatically with no approval needed in between. Steps 3, 5, 6, 7, 8, 9, 10 each end in an explicit approval gate — do not proceed past a gate until the user has approved that step's output.

| # | Skill | Gate after? |
|---|-------|-------------|
| 0 | `topic-scout` (optional — only when no seed topic yet) | **yes — topic pick, before research spend begins** |
| 1 | `trend-retrieve` | no |
| 2 | `serp-analyze` | no |
| 3 | `idea-refine` | **yes — 1st approval** |
| 4 | `fact-enrich` | no |
| 5 | `outline` | **yes — 2nd approval** |
| 6 | `asset-metadata` | **yes — 3rd approval** |
| 7 | `draft-write` | **yes — 4th approval** |
| 8 | `image-generate` | **yes — 5th approval** (runs per asset — a Generated-type asset without a Visual Identity section/backend, or a Diagram/capture-type asset without a usable source, falls back to manual handoff rather than skipping the whole step — see the skill) |
| 9 | `thumbnail-copy` | **yes — 6th approval** (skip if the project renders no hand-written thumbnail copy — see the skill) |
| 10 | `seo-vet` | **yes — final approval** |

`asset-metadata` only plans which images are needed and where — actual prompt-finalization and generation happen in `image-generate`, which now runs after `draft-write` on purpose: grounding prompts in the finished body avoids guessing at a concept from the outline alone and avoids generating images for sections that get cut or reshaped while drafting. `thumbnail-copy` runs after the draft for the same reason: its copy must be grounded in the finished body, not the title. Skip it only when the constitution says thumbnails carry no hand-written copy. `seo-vet` may itself offer to invoke `knowledge-capture` before its final approval — that's expected, not a deviation from the plan.

## Rules

- Never skip a gate. If the user's initial request already contains enough detail to answer a later step's questions, still run every step in order and surface those answers there — don't shortcut the sequence.
- If the user interrupts mid-pipeline with a change (e.g., "actually make it about X instead"), treat that as a revision to whichever step is currently active, re-run that step's approval, and only then continue.
- Communicate with the user in whatever language the constitution or the user's own messages establish — this file itself doesn't dictate that.
- Committing or publishing the resulting file is a separate action the user takes after the final approval — this pipeline's job ends at "vetted and approved," not at "pushed."
