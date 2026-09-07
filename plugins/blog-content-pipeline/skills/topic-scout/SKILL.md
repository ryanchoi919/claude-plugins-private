---
name: topic-scout
description: Step 0 of the content pipeline (optional) — when there is no seed topic yet, scan the knowledge base and the web in parallel for post-worthy candidates, dedupe against existing posts, rank them, and wait for human approval before handing the chosen one to trend-retrieve as its seed topic. Use when starting a pipeline run (including an unattended/scheduled one) with no seed topic given.
---

# Topic Scout

Step 0 of the content pipeline, run only when nobody has handed the pipeline a seed topic yet. Its job is to find candidates, not to decide — it always stops at an approval gate and hands `trend-retrieve` whichever topic the human picks.

Skip this skill entirely if a seed topic is already in hand (a human gave one, or a prior run of this skill already produced an approved pick). In that case, start directly at `trend-retrieve`.

## Prerequisite

Confirm `CONSTITUTION.md` exists at the project root (or, in a monorepo that hosts multiple blogs, at the root of each blog). If none exists anywhere, stop and tell the user to run the `constitution` skill first — this skill needs the Audience and Content Taxonomy sections to judge whether a candidate fits, and the Knowledge Base section to know whether/where to scan.

If the repo contains a single `CONSTITUTION.md`, there is one blog ("brand") and every candidate belongs to it. If it's a monorepo with multiple `CONSTITUTION.md` files (one per blog under its own subdirectory), repeat the steps below once per blog and merge the results into one ranked list, tagging each candidate with its blog's name — this is what lets a scheduled run pick "what to write, and for which blog" with no human involved yet.

## Steps

1. **Locate the posts directory** for whichever blog(s) are in scope. Default to whatever base path `idea-refine` uses for that project (`content/posts/{category}/{slug}/`, or the constitution's own equivalent) — adjust if the constitution specifies something else. List existing post titles/slugs there; this is the dedupe reference for both sources below.

2. **Run the two sources in parallel** — they're independent and there's no reason to serialize them:

   - **Source A — knowledge/ scan (cheap, pre-researched).** Only applies if the constitution's Knowledge Base section defines a path (skip this source entirely if it says "Not used" — fall back to Source B alone). List the entries under that path (title, category, tags, summary) and compare each against the existing post titles/slugs from step 1. An entry counts as "already covered" if some existing post's title or body topic clearly maps to it — not just a keyword overlap; skim the post if the title alone doesn't settle it. Keep every entry that isn't already covered as a candidate: its topic is the entry's subject, its rationale is "already curated and verified in the knowledge base under `<category>/<slug>.md`, not yet written up," and its target blog/brand and audience persona come from matching the entry's category/tags against the constitution's Content Taxonomy and Audience sections.
   - **Source B — web search (broad, noisy).** Use whichever research tool `trend-retrieve` would use, in the same priority order: a Perplexity or other research-oriented MCP tool if connected, otherwise `WebSearch`. Cost-control rule: one comprehensive query per persona/pillar combination worth checking, not many small ones — e.g., "what are the current trending questions/news/searches right now that persona X would care about around pillar Y, that a blog like this hasn't already covered." Scope the query with the constitution's Audience personas and Content Taxonomy pillars so results are on-topic rather than generic trending news. For each candidate this turns up, note why it's timely (a spike, a news hook, a recurring seasonal pattern) — this is what makes it a "2nd-tier, needs scoring" candidate rather than an evergreen one.

3. **Dedupe against existing posts.** Re-check every candidate from both sources against the full existing post list from step 1, not just each source's own quick check — a knowledge-base entry and a web result can independently collide with the same already-published post. Drop anything that's a clear match (same core topic, even if the title wording differs). When a candidate is a plausible *follow-up* to an existing post (a deeper angle, a sequel, an update) rather than a duplicate, keep it but say so in its rationale.

4. **Optional trend signal for Source B candidates**: this plugin ships a self-contained helper script (no project setup needed — it declares its own dependency inline and runs via `uv run`). For at most the top 3-5 web-sourced candidates still standing, attempt once each:
   - Decide `--geo` the same way `trend-retrieve` does: the constitution's Audience section names a country/region → that ISO 3166-1 alpha-2 code; otherwise omit `--geo`.
   - Run: `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/keyword_trends.py" related --seed "<candidate topic>" [--geo <code>]`.
   - Its `top`/`rising` output is a 0-100 relative index, never an absolute search count — use it only to break ties in the ranking below, never state it as a search-volume figure.
   - If `uv` isn't available, or the command fails for any reason, skip this signal silently and continue — it's optional, never a required input.

5. **Rank and present the candidate list.** For every surviving candidate, show at minimum: the topic, its source (knowledge/ or web), the target blog/brand (if multi-blog) and audience persona, and a one-line rationale (why it fits, why it's timely, or why it's a natural follow-up). Order by a mix of fit-to-audience, freshness of the underlying signal, and how cheap the next steps will be (a knowledge/-sourced candidate needs less fact-finding than a raw web trend) — say briefly why the top few are ranked where they are, don't just dump an unordered list.

6. **Approval gate — wait for the human to pick.** Present the ranked list and stop:
   > "다음 후보들을 찾았습니다. 이 중 하나를 골라주시거나, 다른 주제를 직접 알려주세요."
   Do not auto-select the top candidate, even in an unattended/scheduled run — this gate exists specifically so a human confirms the topic before any research spend happens downstream, the same as every other gate in this pipeline. If nothing on the list is good, that's a valid outcome too: say so and wait for the human to supply their own seed topic instead.

7. **Handoff.** Once the human names their pick (by number, or their own topic), proceed directly into `trend-retrieve` using that pick as its seed topic — no separate gate here, since step 6 already served that purpose. If the pick came from Source A, mention to `trend-retrieve`/`fact-enrich` downstream that a knowledge-base entry already exists for it, so they can treat it as a trusted source rather than re-researching from scratch.
