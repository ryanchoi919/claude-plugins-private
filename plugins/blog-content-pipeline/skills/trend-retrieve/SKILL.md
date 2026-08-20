---
name: trend-retrieve
description: Step 1 of the content pipeline — research real reader pain points and trending needs around a seed topic. Use when starting a new post and no research has been done yet.
---

# Trend Retriever

First step of the content pipeline. Given a seed topic or keyword, find out what the target audience is actually struggling with, using real research rather than assumption.

## Steps

1. Read `CONSTITUTION.md` at the project root. If it doesn't exist, stop and tell the user to run the `constitution` skill first — every downstream step depends on knowing the audience and voice.
2. From the constitution's Audience section, identify which persona this seed topic is for.
3. Research the real pain points, confusions, or unmet needs this persona has around the seed topic. Use whichever research tool is available in this environment, in this priority order:
   - A Perplexity or other research-oriented MCP tool, if connected
   - `WebSearch` + `WebFetch` otherwise
4. Cost-control rule: compose **one** comprehensive query/prompt rather than several small ones. Ask for everything you need in a single pass — e.g., "What are the top 3 pain points persona X faces with topic Y, and what are the top 3 things they'd need to know or say to handle it?"
5. Optional trend signal: check whether this project has `scripts/keyword_trends.py` (e.g. `ls scripts/keyword_trends.py`). If it exists:
   - Decide `--geo`: if the constitution's Audience section names a specific country/region for the readers, use that country's ISO 3166-1 alpha-2 code (e.g. `--geo KR`); otherwise omit `--geo` entirely (worldwide).
   - Run once: `python scripts/keyword_trends.py related --seed "<seed topic>" [--geo <code>]`.
   - Its JSON output (`top`/`rising` related queries) reflects Google's actual relative search interest — fold any genuinely new phrasing or derived interest it surfaces into the pain points from step 3. It is a 0-100 relative index, never an absolute search count — do not describe it as one.
   - If the script doesn't exist in this project, or its output is `{"error": ...}`, skip this signal silently and continue — it's optional tooling this project may not have, not a required input.
6. Do not report back yet — hold the findings in context and proceed directly to the `serp-analyze` skill. No user approval is needed at this stage (the first approval gate is after `idea-refine`).
