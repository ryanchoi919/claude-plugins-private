---
name: post
description: Draft maker-community posts (e.g. Disquiet in Korean, Indie Hackers in English, or any other platform listed in VOICE.md) from a product update — a source file path, pasted text, or a free-text description of what shipped. Reads marketing/community-posts/VOICE.md for voice/links/tags, drafts each platform's post, pauses for approval, then saves each approved draft under marketing/community-posts/posts/<platform>/ with YAML frontmatter tracking status. Use when the user wants to write or share a community update post.
---

# Post

Drafts one community-update post per platform listed in the project's `marketing/community-posts/VOICE.md` (typically Disquiet in Korean and Indie Hackers in English) from a single piece of source material. Ends at an approved, saved draft — actually publishing to each platform is a manual step the user takes afterward, since this plugin has no API or browser access to either service.

## Prerequisite

Confirm `marketing/community-posts/VOICE.md` exists at the project root. If it doesn't, stop and run the `voice` skill first. This skill does not improvise tone, links, or tags — those live in VOICE.md.

## When invoked

1. **Get source material**, in priority order:
   - If the user pointed at a specific file (e.g. an update-log entry) or pasted text, use that directly.
   - Else, if VOICE.md's "Source Content" section names a directory, find the most recently dated entry there and confirm with the user that it's the right one before drafting (don't assume silently).
   - Else, ask the user directly what shipped or what this post should cover.
2. **Draft each platform**, one at a time, using that platform's section in VOICE.md (voice, structure, tags, must-avoid, CTA pattern):
   - Don't just translate one draft into the other language — each platform gets its own opening hook and structure per VOICE.md, even when covering the same underlying update.
   - Reuse the product one-liner(s) and links from VOICE.md verbatim rather than re-deriving them.
   - If the user asks for only one platform, draft only that one — don't force every platform every time.
3. **Approval gate.** Show all drafted platforms together and ask for changes. Iterate until the user approves. Do not save anything before approval.
4. **Save.** Once approved, write each platform's final draft to its own file at `marketing/community-posts/posts/<platform>/<YYYY-MM-DD>-<slug>.md`, where `<platform>` is that section's `Folder key` field in VOICE.md and `<slug>` is a short kebab-case label derived from the update's topic (not from the date). Create the platform directory if it doesn't exist yet. Each file starts with YAML frontmatter, then the post body:

   ```markdown
   ---
   platform: <platform>
   slug: <slug>
   created: <YYYY-MM-DD>
   status: draft
   url:
   source: <path or short description of the source material used>
   ---

   <post body>
   ```

   Report the saved paths and stop.

## Rules

- Never call an external posting API or attempt browser automation to actually publish — this skill's job ends at "approved and saved," the same boundary `draft-write` in blog-content-pipeline draws at a vetted draft rather than a merge. Once the user has actually posted it somewhere, the `mark-published` skill records that — this skill only ever writes `status: draft`.
- If VOICE.md lists a platform this skill has no built-in familiarity with, still draft it using VOICE.md's own section for that platform — don't skip it, and don't invent generic filler for platforms VOICE.md is silent on.
- Keep each platform draft self-contained (no "same as above" shorthand) — the saved file is meant to be copy-pasted straight into that platform's editor, frontmatter excluded.
