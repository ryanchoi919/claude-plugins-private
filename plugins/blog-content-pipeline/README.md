# blog-content-pipeline

A Claude Code plugin that turns a seed topic into a publish-ready blog post through a constitution-driven, approval-gated pipeline: trend research → SERP gap analysis → idea refinement → fact enrichment → outline → asset/metadata planning → image generation → draft writing → thumbnail copy → SEO/brand vetting → optional knowledge-base capture.

It's designed to be dropped into *any* blog repo, not just one specific blog. None of the skills hardcode a brand voice, taxonomy, or formatting rules — they all read a `CONSTITUTION.md` file at the target project's root. Write a different constitution, get a differently-voiced blog out of the same pipeline.

## Install

This repo is both a plugin and a self-hosted marketplace (`.claude-plugin/marketplace.json` points at the plugin in the repo root).

```
/plugin marketplace add ryanchoi919/blog-content-pipeline
/plugin install blog-content-pipeline@blog-content-pipeline
```

Since this is a private repository, Claude Code needs GitHub access to fetch it — make sure you're authenticated (e.g. `gh auth status`) or set a `GITHUB_TOKEN` with repo read access in the environment where you run `/plugin marketplace add`.

## Usage

1. In the target blog repo, run the `constitution` skill first if `CONSTITUTION.md` doesn't exist yet. Answer its interview honestly — every other skill depends on it.
2. Run `write-post` (or invoke it implicitly by asking to write a post) to drive the full 10-step pipeline. It pauses at 7 approval gates: after idea refinement, after the outline, after asset/metadata, after image generation, after the draft, after thumbnail copy, and at final SEO vetting.
3. Each individual step is also its own skill (`trend-retrieve`, `serp-analyze`, `idea-refine`, `fact-enrich`, `outline`, `asset-metadata`, `image-generate`, `draft-write`, `thumbnail-copy`, `seo-vet`, `knowledge-capture`) if you want to re-run or resume a single stage instead of the whole pipeline.

## Skills

| Skill | Role |
|---|---|
| `constitution` | Sets up/updates `CONSTITUTION.md` — brand, audience, voice, taxonomy, formatting rules, growth mechanics, knowledge base |
| `write-post` | Master orchestrator — runs the full pipeline in order |
| `trend-retrieve` | Step 1 — research real audience pain points around a seed topic |
| `serp-analyze` | Step 2 — find the content gap versus what's already ranking |
| `idea-refine` | Step 3 — concrete post plan + **1st approval gate** |
| `fact-enrich` | Step 4 — verify and enrich facts against the knowledge base |
| `outline` | Step 5 — H1-H3 structure + FAQ + **2nd approval gate** |
| `asset-metadata` | Step 6 — visual asset plan + frontmatter + **3rd approval gate** |
| `image-generate` | Step 7 — generate approved in-body illustrations via a configured backend + **4th approval gate** |
| `draft-write` | Step 8 — full draft in brand voice + **5th approval gate** |
| `thumbnail-copy` | Step 9 — hand-written thumbnail/hero display copy, grounded in the draft + **6th approval gate** |
| `seo-vet` | Step 10 — final checklist vetting + **7th (final) approval gate** |
| `knowledge-capture` | On-demand — file a reusable fact into the project's knowledge base, cross-linked |

## Origin

Ported and generalized from a blog-specific (Eroun Labs / korean-edu) 8-step content pipeline originally written for the Antigravity agent. The step logic and approval-gate structure are preserved; brand specifics were extracted into the `CONSTITUTION.md` convention so the same pipeline works for any blog.
