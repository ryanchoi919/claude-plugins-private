---
name: thumbnail-copy
description: Step 10 of the content pipeline — write the short display copy that gets rendered on the post's thumbnail/hero image, grounded in the finished draft, and get approval. Use right after lead-magnet, before seo-vet. Skip if the project doesn't render hand-written copy on its thumbnails.
---

# Thumbnail Copy

Tenth step of the content pipeline, and an **approval gate**. Runs after `draft-write` (and after `lead-magnet`, if this project has one) because good thumbnail copy has to be grounded in the actual body — not guessed from the title.

## When this applies

Only if the project renders **hand-written display copy on the thumbnail/hero image** (check `CONSTITUTION.md`). Many projects don't — they use a title-only card, a photo, or no image text. If the constitution says thumbnails carry no hand-written copy, **skip this step entirely** and go straight to `seo-vet`.

The thumbnail display copy is a **separate artifact from the frontmatter SEO title**: shorter, split across 2-3 lines, rendered as an image (so search engines can't read it — its whole job is the human click). It is NOT the title truncated.

## Inputs

- The approved draft body (this is why the step runs here — you read it).
- The post's `targetAudience` (the specific reader, from `idea-refine` / frontmatter).
- The frontmatter `title` (for reference, not to copy).
- The constitution's own title/thumbnail rules (length/line limits, banned phrasing, language gotchas, and **where the copy is stored** — a frontmatter field, a build-script array, etc.). Project rules there always **override** the general method below.

## Method

Pin the reader first, then run each candidate through the 4+1 model, then the compression checklist. Write copy FOR the `targetAudience` so they think "this is me" — not a third-person observer voice ("people who…").

### 4+1 reader model

1. **Recognition** — a concrete situation/symptom the reader sees themselves in, not a topic noun.
2. **Tension** — a real gap between expectation and reality, or a reason worth knowing.
3. **Payoff signal** — some answer to "why read this," in every card, whatever the genre. Prescriptive posts get an explicit "how to / guide / method"; diagnostic/explanatory posts get an expectation-vs-reality twist, a named consequence, or a promise the cause is non-obvious; comparison posts signal that an alternative exists — centered on the actual concept the post delivers, never on cheap-shotting a competitor. A card that only restates the topic/problem with no hint of what the reader gets ("so what?") fails, regardless of genre.
4. **Credibility** — a number, a named audience, or an explicit comparison target lowers click risk.
5. **Zero-context parseability** — the card shows 2-3 lines with no body around them. No jargon/acronym standing alone without context; the lines must make sense read by themselves.

### Hook energy (~10-20%)

A purely honest, flat card doesn't earn the click. Add a little more pull than plain information: a question hook, a curiosity gap ("the real reason"), a concrete vivid symptom over an abstract one, the sting of repetition ("again", "still"). Thumbnail copy may carry a bit more of this than body prose. But hook energy is **tone, not distortion** — never (a) over-promise or claim something the body doesn't support, (b) use hype clichés the constitution bans, (c) cheap-shot a competitor. If a punchier phrasing is only true "if you squint," pull it back.

### Compression integrity checklist (0 is the precondition for the rest)

0. **Before compressing, write the full, elision-free sentence the card is compressing** (real subject, real verb), and confirm it is something the **draft body actually says or directly supports** — read the body, don't reconstruct "what the post means" from the title or memory. Compress from that verified sentence, not from a previous compressed draft: if a reviewer flags one problem, re-derive the whole line from the full sentence again — patching one spot while reusing the rest is how a second, unrelated flaw slips in. Also confirm the verb actually collocates with its object (e.g. a rate/percentage is *calculated/tracked*, not "counted" — that verb is for discrete countable things; check the equivalent in whatever language you're writing).
1. The original's core predicate (cause/effect, active/passive) survives the compression.
2. The lines read cleanly on their own, with no body or subtitle to lean on.
3. Any specialized term in the lead makes sense to a reader who doesn't know it — otherwise swap in plain wording.
4. If the title carries a cause+solution structure, split it across lines (one = cause, one = payoff); don't drop the solution half.
5. Quantifiers ("three", "3") don't get buried inside a compound noun where it's unclear what's being counted — put them before the single noun they count, or after the whole phrase.
6. **Read adjacent lines concatenated as one utterance** — not each line in isolation. If a line ends in a connective/particle that grammatically demands a specific continuation (contrast, condition, a predicate about its topic), the next line must actually deliver it, not an unrelated label swapped in to hit a length limit. (Language-specific; the constitution may document the exact gotchas.)
7. Don't join two abstract nouns with "becomes"/"instead of" and strip out the subject and concrete verb ("managing the goal becomes managing the system" reads as two activities morphing) — keep the real subject and the concrete verb the source sentence used.

### Length / rendering

Respect the constitution's line limits and however the copy is rendered (some setups auto-fit the font to the width, some hard-cap characters). Write the accurate line first; don't cram a worse phrasing to hit a character count. If a line genuinely can't fit even after the renderer's shrink, shorten the copy rather than accept an overflow or an awkward abbreviation.

## Steps

1. Confirm the project uses hand-written thumbnail copy (else skip to `seo-vet`).
2. For each post, apply the method above and produce the display copy in the project's target language(s), written to (or proposed for) wherever the constitution says it lives.
3. Report the copy to the user and **wait for explicit approval** before proceeding to `seo-vet`. If they ask for changes, re-derive from the full verified sentence (checklist item 0), don't patch.
