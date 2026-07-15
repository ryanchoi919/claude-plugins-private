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
5. Do not report back yet — hold the findings in context and proceed directly to the `serp-analyze` skill. No user approval is needed at this stage (the first approval gate is after `idea-refine`).
