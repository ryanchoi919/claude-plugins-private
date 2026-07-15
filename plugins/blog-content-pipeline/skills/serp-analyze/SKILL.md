---
name: serp-analyze
description: Step 2 of the content pipeline — analyze competing search results and existing content to find the gap this post should fill. Use right after trend-retrieve, before any drafting begins.
---

# SERP Analyzer

Second step of the content pipeline. Turns the pain points found in `trend-retrieve` into a concrete content gap versus what's already ranking.

## Steps

1. From the pain points gathered in `trend-retrieve`, define the actual search queries the audience would type (not just the seed topic — the literal phrasing a searcher would use).
2. Run a web search (`WebSearch`) for those queries and identify the top-ranking pages.
3. Fetch and actually read the top few results (`WebFetch`), not just their snippets. Look for:
   - What they get wrong, oversimplify, or leave out
   - Where they're generic/official-tone versus grounded in the lived reality the audience actually faces
   - Any secondary/local sources (forums, local-language sites, review platforms) that surface a reality the top English-language results miss — search those too if the constitution's audience implies a language/culture gap
4. Re-read `CONSTITUTION.md`'s Voice & Tone and Mission sections. Frame the gap in terms of this specific blog's angle — the gap that matters is "what this blog's audience needs that the top-ranking pages don't give them," not a generic SEO gap.
5. Produce a short, explicit **content gap statement**: what's missing, and why this blog is positioned to fill it.
6. Do not report back yet — proceed directly to `idea-refine`. No user approval needed at this stage.
