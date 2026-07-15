---
name: idea-refine
description: Step 3 of the content pipeline — turn the content gap into a concrete post plan (title candidates, target keyword, lead magnet, differentiator) and get first-gate approval from the user. Use right after serp-analyze.
---

# Idea Refiner

Third step of the content pipeline, and the **first approval gate**. Turns the content gap from `serp-analyze` into a concrete, user-approved plan before any research spend or writing happens.

## Steps

1. Create the post's dedicated working folder: `content/posts/{category}/{slug}/sources/` (adjust the base path if the constitution specifies a different content directory). `{category}` must be one of the categories listed in `CONSTITUTION.md`'s Content Taxonomy.
2. Ask the user to drop any reference material into that `sources/` folder — source textbooks, screenshots, existing data, prior drafts — before planning continues:
   > "If you have any reference material for this topic (source documents, screenshots, data, prior notes), drop it in `content/posts/{category}/{slug}/sources/` now and reply 'ready' — or reply 'no sources' to skip."
3. If sources were uploaded, check what's there. For any large file (roughly 50+ pages), don't read it cover to cover — check its table of contents/index first and ask the user which sections actually matter before doing a targeted read.
4. Treat anything in `sources/` as the highest-trust input for planning — it outranks the general research from `trend-retrieve` and `serp-analyze` when they conflict.
5. Think through the plan carefully before presenting it — deliberately look for the obvious, generic version of this post and figure out what would make it not that. Produce:
   - 3-5 candidate titles (in the target audience's language, matching the constitution's voice)
   - The primary target keyword/phrase
   - A lead magnet concept, if the constitution's Growth Mechanics section uses lead magnets
   - The concrete differentiator versus the SERP gap identified in step 2
   - Whether/how any uploaded sources shaped the plan
6. Report this plan to the user and **wait for explicit approval**. Do not proceed to `fact-enrich` until the user approves — if they ask for changes, revise and re-present.
