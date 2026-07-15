---
name: voice
description: Set up or update this project's marketing/community-posts/VOICE.md — product one-liners, per-platform tone rules (Disquiet, Indie Hackers, ...), recurring links/tags, and maker identity that the `post` skill reads before drafting anything. Use when a project has no VOICE.md yet, or when brand/voice/link rules need to change.
---

# Voice

The `post` skill in this plugin is platform-agnostic by design: it doesn't hardcode a product's one-liner, a platform's tone, or a link set. Instead it starts by reading `marketing/community-posts/VOICE.md` at the project root. This skill creates or updates that file.

This is what makes the plugin portable across unrelated products: the same plugin, installed into two different repos, produces differently-voiced posts because it reads two different VOICE.md files. It mirrors the same idea as a blog's `CONSTITUTION.md`, scoped to maker-community posting instead of blog content.

## When invoked

1. Check whether `marketing/community-posts/VOICE.md` exists at the project root.
   - If it exists, read it, summarize it back to the user in a few lines, and ask what should change.
   - If it does not exist, interview the user to fill in every section below. Don't invent product facts, links, or a maker identity — ask. It's fine to leave a section as `TBD` if the user genuinely hasn't decided yet, but flag which sections are still open.
2. Write (or update) `marketing/community-posts/VOICE.md` using the template below.
3. Report a short diff/summary and stop — do not chain into the `post` skill automatically. The user decides when to start drafting posts.

## Template

```markdown
# <Product Name> — Community Post Voice

## Product
- One-liner (ko): <...>
- One-liner (en): <...>
- Stage: <e.g., pre-launch / waitlist / launched / revenue-generating>
- Website: <url>
- Signup / waitlist link: <url, if different from website>

## Source Content
- Where update/changelog entries live: <path relative to repo root, or "none — ask each time">
- Format notes: <e.g., which frontmatter fields to read — title, date, description>

## Maker Identity
- Name/nickname to use in posts: <...>
- Solo or team: <...>
- Tone when talking about self: <e.g., first person, humble/curious framing rather than corporate "we">

## Platforms

### <Platform 1 name, e.g. Disquiet>
- Folder key: <lowercase kebab-case used under marketing/community-posts/posts/ — e.g. disquiet>
- URL domain: <e.g., disquiet.io — used by `mark-published` to infer which platform a pasted URL belongs to>
- Language: <...>
- Voice: <e.g., personal maker-log tone, not marketing copy>
- Structure: <e.g., hook -> one-liner -> progress timeline -> what's next -> CTA>
- Tags: <...>
- Must avoid: <...>
- CTA pattern: <e.g., end with a question that invites comments>

### <Platform 2 name, e.g. Indie Hackers>
- Folder key: <...>
- URL domain: <...>
- Language: <...>
- Voice: <...>
- Structure: <...>
- Tags: <...>
- Must avoid: <...>
- CTA pattern: <...>

<!-- add one more ### section per additional platform (BetaList, WIP, Peerlist, ...) as they're adopted -->

## Recurring Links & Handles
- Website: <...>
- X/Twitter: <...>
- GitHub: <...>
```

## Notes for the interview

- If past drafts, or this conversation's history, already establish a tone for a platform, read those first and propose a VOICE.md draft from them, then confirm with the user — don't restart from a blank interview when the tone is already established.
- Don't skip straight to generic boilerplate — the whole point of this file is to be specific enough that `post` can apply it without asking the user to re-explain tone every time.
- Keep the file itself terse — it's re-read on every `post` run, so bloat here costs tokens on every future post.
