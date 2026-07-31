---
name: constitution
description: Set up or update this project's CONSTITUTION.md — the brand voice, audience, taxonomy, and formatting rules that every other skill in this plugin reads before doing its job. Use when a blog project has no CONSTITUTION.md yet, or when brand/voice/format rules need to change.
---

# Constitution

Every other skill in this plugin (`trend-retrieve`, `serp-analyze`, `idea-refine`, `fact-enrich`, `outline`, `asset-metadata`, `image-generate`, `draft-write`, `thumbnail-copy`, `seo-vet`, `knowledge-capture`) is content-agnostic by design: none of them hardcode a brand, a voice, or a formatting convention. Instead, each one starts by reading `CONSTITUTION.md` at the project root. This skill creates or updates that file.

This is what makes the pipeline portable across unrelated blogs: the same plugin, installed into two different repos, produces two very different-sounding posts because it reads two different constitutions.

## When invoked

1. Check whether `CONSTITUTION.md` exists at the project root.
   - If it exists, read it, summarize it back to the user in a few lines, and ask what should change.
   - If it does not exist but scattered brand docs do (a style guide, a growth strategy doc, an old brand identity doc), read those first and draft the constitution from them, then confirm with the user.
   - If it does not exist and there are no scattered docs either (blank-slate case), don't run a raw section-by-section interview. Instead, pick the closest-matching example from the **Blank-slate scaffold** below, adapt its category/platform placeholders to whatever the user has already mentioned about the project, and present the filled-in draft for the user to correct rather than write from scratch. Don't invent brand facts — ask. It's fine to leave a section as `TBD` if the user genuinely doesn't know yet, but flag which sections are still open.
2. Write (or update) `CONSTITUTION.md` using the template below.
3. Report a short diff/summary and stop — do not chain into any other skill automatically. The user decides when to start writing posts.

## Template

```markdown
# <Brand Name> — Constitution

## Mission
<1-2 sentences: what this blog is, and the gap it fills that competitors don't>

## Audience
- <persona 1: who they are, what they're trying to do>
- <persona 2>
- <persona 3, if applicable>

## Voice & Tone
- Persona: <e.g., "a friendly 1:1 local buddy", "a strict but caring tutor">
- Must avoid: <e.g., dry AI-explainer tone, phrases like "In Korea, there is...">
- Signature move: <a line or device this blog always does — e.g., always frames advice around a scene the reader will actually experience>
- Example line: "<one real sentence in the target voice, so future writers can pattern-match>"

## Content Taxonomy
- Pillars: [<pillar 1>, <pillar 2>, ...]
- Categories: [<category-slug-1>, <category-slug-2>, ...]  (used in frontmatter `categories`)
- Planned series (optional): [<S1: name>, <S2: name>, ...]

## Formatting Rules
- Platform/framework: <e.g., Hugo (Blowfish theme), Ghost, WordPress>
- Frontmatter schema (required fields): <list each field and its exact format/type>
- Custom components/shortcodes (if any): <name -> usage syntax, one per line>
- Admonition/callout syntax: <e.g., GitHub-style `> [!tip]`; note anything that's explicitly forbidden, e.g. a shortcode that breaks the build>
- Multi-language mapping format (if the blog teaches a language): <e.g., native text + romanization (italic) + English translation, each on its own line>
- Anything else that would break the build if violated: <list>

## Visual Identity
- Illustration style: <e.g., flat vector illustration, isometric, watercolor, photographic — the visual equivalent of the Voice & Tone persona>
- Palette: <hex codes or named colors to use>
- Mood: <e.g., warm and inviting, minimal and clean, playful>
- Must avoid: <e.g., text baked into the image, stock-photo look, realistic human faces>
- Generation backend (optional): <e.g., "AUTOMATIC1111 WebUI at $SD_WEBUI_URL", "Adobe Firefly MCP", "none — hand off to designer">
- Only fill this in if the blog generates in-body illustrations (see the `image-generate` skill). If illustrations are hand-made or not used, write "Not used."

## Growth Mechanics
- Lead magnet pattern: <what a lead magnet looks like for this blog, if any>
- CTA pattern: <where/how a CTA appears in a post>
- Publishing cadence: <e.g., 2x/week, pillar + supporting post rotation>
- Primary SEO approach: <e.g., long-tail keywords first>

## Knowledge Base (optional)
- Path: <e.g., knowledge/>
- Categories: [<category 1>, <category 2>, ...]  (used by the `knowledge-capture` skill)
- Only fill this in if the project accumulates reusable domain facts across posts. If the blog doesn't need this, write "Not used."
```

## Blank-slate scaffold

Use this when there is no `CONSTITUTION.md` and no scattered brand docs to draft from. It's a filled-in example for the most common case this plugin sees (a solo technical blog) — present it as a draft, then let the user correct whatever doesn't fit instead of asking each field cold.

```markdown
# Example Dev Blog — Constitution

## Mission
Practical write-ups for developers hitting a specific error or decision, written by someone who just solved it — not a marketing site.

## Audience
- A developer who landed here from a search engine with one specific error message or task
- A returning reader who wants the same author's take on a new tool

## Voice & Tone
- Persona: a peer developer sharing what just worked, not a formal technical writer
- Must avoid: dry AI-explainer tone, restating the obvious ("In this post, we will..."), hedging every claim
- Signature move: opens with the exact symptom/error the reader searched for, then the fix, then the why
- Example line: "This threw a nondescript 500 for two hours before I found the actual cause: a stale lockfile."

## Content Taxonomy
- Pillars: [debugging war stories, tool comparisons, how-I-built-X]
- Categories: [backend, tooling, infra]
- Planned series (optional): none yet

## Formatting Rules
- Platform/framework: Hugo (or whatever static site generator the project uses — confirm)
- Frontmatter schema (required fields): title (string), date (ISO 8601), categories (array), summary (string, <160 chars)
- Custom components/shortcodes (if any): none yet
- Admonition/callout syntax: GitHub-style `> [!tip]` / `> [!warning]`
- Multi-language mapping format (if the blog teaches a language): Not used
- Anything else that would break the build if violated: none identified yet

## Visual Identity
- Illustration style: flat vector illustration
- Palette: TBD — confirm brand colors
- Mood: minimal and clean
- Must avoid: text baked into the image, stock-photo look
- Generation backend (optional): none — confirm before enabling image-generate

## Growth Mechanics
- Lead magnet pattern: none yet
- CTA pattern: link to related posts at the end
- Publishing cadence: TBD
- Primary SEO approach: long-tail keywords first

## Knowledge Base (optional)
Not used.
```

Adapt pillars/categories/platform to match whatever the user has already said about the project; everything else is a reasonable default to confirm or overwrite.

## Notes for the interview

- Don't let the final written file stay generic boilerplate — the whole point of this file is to be specific enough that a pipeline skill can apply it without further clarification from the user. The blank-slate scaffold is a starting draft to correct against, not an acceptable end state; every `TBD` and confirm-me placeholder should get resolved or explicitly deferred before you write the file.
- If the user already has scattered brand docs (a style guide, a growth strategy doc, an old brand identity doc), read those first and draft the constitution from them, then confirm with the user rather than starting from a blank interview.
- Keep the file itself terse — it's meant to be re-read by every pipeline skill on every run, so bloat here costs tokens on every future post.
