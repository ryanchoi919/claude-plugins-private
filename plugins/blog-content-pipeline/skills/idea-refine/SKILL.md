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
   - A one-sentence statement of exactly who this single post is for — the specific reader, not the blog's whole audience (e.g. not "people who set goals" but "people who built an elaborate goal system in a tool, then burned out maintaining it"). Write titles and any thumbnail copy FOR that reader so they think "this is me," not in a third-person observer voice about "people who…". If the constitution defines a per-post audience field (e.g. frontmatter `targetAudience`), record it there. Everything below is applied after this reader is pinned down.
   - 3-5 candidate titles (in the target audience's language, matching the constitution's voice). Run each candidate through a reader-motivation check before presenting it:
     - **Recognition**: does it name a concrete situation/symptom the reader sees themselves in, not just a topic noun ("작심삼일" beats "목표 설정")?
     - **Tension**: does it open a real gap between expectation and reality, or a reason worth knowing ("~하는 이유", a genuine question)?
     - **Payoff signal**: every candidate must answer "why read this" in some form — this step is never optional, only its shape changes with the post's genre. Prescriptive posts (how-to, checklist, comparison verdict) get an explicit word like "how to"/"guide"/"method". Diagnostic/explanatory posts don't get that word bolted on (it reads as a mismatch the moment the reader opens it) but still need a payoff — an expectation-vs-reality twist, a named consequence, or a promise that the cause is non-obvious. Comparison posts need a signal that an alternative exists, not just the two things being named — but that signal should center the actual concept/mechanism the post delivers (what specifically is better, and about what), not a vague "there's another way" hedge, and should not hinge on naming a competing product negatively: a competitor can add the missing feature later (breaking the post's shelf life) and loyal users of that product read a cheap-shot claim as reason to distrust the rest of the post. Name the underlying idea instead of the competitor. Test: if a candidate could be read as flatly restating the topic with no hint of what the reader gets from it (a bare declaration), or if it's really just a compressed paraphrase of the title's own nouns rather than the post's actual keyword/answer, it fails this check regardless of genre — rewrite it around what the post is actually teaching, not around shortening the title.
     - **Credibility**: a number, a named audience, or an explicit comparison target lowers the reader's risk of clicking something thin.
     - **Hook energy (~10-20%)**: a purely honest, accurate title often reads flat. Dial in a little more pull than plain information delivery — a question hook, a curiosity gap ("the real reason"), a concrete vivid symptom over an abstract one, the sting of repetition ("again", "still"). A title may carry a bit more of this than body prose, since its job is to earn the click. But hook energy is tone, not distortion — never (a) over-promise or claim something the body doesn't support, (b) use hype clichés the constitution bans, or (c) take a cheap shot at a competitor. If a punchier phrasing would only be true "if you squint," it's too far; pull it back.
   - Note: the short display copy that gets rendered on a thumbnail/hero image (if the project uses one) is a **separate artifact from this SEO title** and is authored later, in the `thumbnail-copy` step — after the draft exists, since good thumbnail copy has to be grounded in the actual body. Don't try to finalize thumbnail copy here; just make the title itself strong.
   - The primary target keyword/phrase
   - A lead magnet concept, if the constitution's Growth Mechanics section uses lead magnets
   - The concrete differentiator versus the SERP gap identified in step 2
   - Whether/how any uploaded sources shaped the plan
6. Report this plan to the user and **wait for explicit approval**. Do not proceed to `fact-enrich` until the user approves — if they ask for changes, revise and re-present.
