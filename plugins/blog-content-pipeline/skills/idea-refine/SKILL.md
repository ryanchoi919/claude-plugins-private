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
   - 3-5 candidate titles (in the target audience's language, matching the constitution's voice). Run each candidate through a reader-motivation check before presenting it:
     - **Recognition**: does it name a concrete situation/symptom the reader sees themselves in, not just a topic noun ("작심삼일" beats "목표 설정")?
     - **Tension**: does it open a real gap between expectation and reality, or a reason worth knowing ("~하는 이유", a genuine question)?
     - **Payoff signal**: every candidate must answer "why read this" in some form — this step is never optional, only its shape changes with the post's genre. Prescriptive posts (how-to, checklist, comparison verdict) get an explicit word like "how to"/"guide"/"method". Diagnostic/explanatory posts don't get that word bolted on (it reads as a mismatch the moment the reader opens it) but still need a payoff — an expectation-vs-reality twist, a named consequence, or a promise that the cause is non-obvious. Comparison posts need a signal that an alternative exists, not just the two things being named. Test: if a candidate could be read as flatly restating the topic with no hint of what the reader gets from it (a bare declaration), it fails this check regardless of genre — rewrite it, don't leave it as-is because "this genre doesn't need a resolution word."
     - **Credibility**: a number, a named audience, or an explicit comparison target lowers the reader's risk of clicking something thin.
     If the post also needs a separate short-form/thumbnail copy derived from the title (check the constitution for this), that copy must preserve the title's actual causal relationship — don't invent a solution the title doesn't contain, and don't drop a solution clause the title does contain by only carrying forward the setup half. It should also make sense read with zero surrounding context, since short-form copy rarely gets a subtitle to lean on. When that copy is split across multiple short lines/fragments, read them concatenated as one utterance, not just each fragment in isolation — if one fragment ends in a connective or particle that grammatically demands a specific kind of continuation (contrast, condition, a predicate about its topic), confirm the next fragment actually supplies that, rather than swapping in an unrelated topical label that happens to fit the length limit. If the constitution defines its own title/thumbnail-copy rules (length limits, banned phrasing, taxonomy pillars, language-specific grammar gotchas), those take precedence over this general check.
   - The primary target keyword/phrase
   - A lead magnet concept, if the constitution's Growth Mechanics section uses lead magnets
   - The concrete differentiator versus the SERP gap identified in step 2
   - Whether/how any uploaded sources shaped the plan
6. Report this plan to the user and **wait for explicit approval**. Do not proceed to `fact-enrich` until the user approves — if they ask for changes, revise and re-present.
