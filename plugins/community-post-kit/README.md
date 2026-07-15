# community-post-kit

A Claude Code plugin that drafts maker-community posts (Disquiet, Indie Hackers, and any other platform you add) from a product's own update notes.

It's designed to be dropped into *any* product repo, not just one specific product. No skill hardcodes a one-liner, a platform's tone, or a link set — all of them read a `marketing/community-posts/VOICE.md` file at the target project's root. Write a different VOICE.md, get differently-voiced posts out of the same plugin.

Publishing itself stays manual: this plugin has no API or browser access to Disquiet, Indie Hackers, or any other platform. Its job ends at an approved, saved draft file — copy-pasting it into each platform's editor is on you.

## Install

This repo is both a plugin and a self-hosted marketplace (`.claude-plugin/marketplace.json` points at the plugin in the repo root).

```
/plugin marketplace add ryanchoi919/community-post-kit
/plugin install community-post-kit@community-post-kit
```

Since this is a private repository, Claude Code needs GitHub access to fetch it — make sure you're authenticated (e.g. `gh auth status`) or set a `GITHUB_TOKEN` with repo read access in the environment where you run `/plugin marketplace add`.

## Usage

1. In the target repo, run the `voice` skill first if `marketing/community-posts/VOICE.md` doesn't exist yet. Answer its interview honestly — every other skill depends on it for tone, links, tags, and (for `mark-published`) each platform's URL domain.
2. Run `post` whenever you have an update to share — point it at a specific update-log file, paste the update text, or just describe what shipped. It drafts every platform listed in VOICE.md, pauses for your approval, and saves each approved draft to `marketing/community-posts/posts/<platform>/<date>-<slug>.md` with `status: draft` in its frontmatter.
3. Copy each saved draft into the corresponding platform yourself. This plugin never posts on your behalf.
4. Once a post is actually live, run `mark-published` with the URL. It finds the matching file (matching the URL's domain to a platform, then confirming with you which draft it is) and flips its frontmatter to `status: published` with the URL and publish date recorded.

## File layout

```
marketing/community-posts/
  VOICE.md
  posts/
    disquiet/
      2026-07-15-templates-update.md
    indie-hackers/
      2026-07-15-templates-update.md
```

Each post file is frontmatter + body:

```markdown
---
platform: disquiet
slug: templates-update
created: 2026-07-15
status: draft   # -> published, once mark-published runs
url:
source: apps/website/src/content/updates/ko/2026-07-templates.md
---

<post body>
```

## Skills

| Skill | Role |
|---|---|
| `voice` | Sets up/updates `marketing/community-posts/VOICE.md` — product one-liners, maker identity, source-content location, and per-platform voice/structure/tags/CTA/URL-domain rules |
| `post` | Drafts one post per platform from a source update, gates on approval, then saves each approved draft to its own frontmatter'd file under `posts/<platform>/` |
| `mark-published` | Given a live post's URL, finds the matching draft file and updates its frontmatter status/url/published_at |

## Origin

Sibling to [`blog-content-pipeline`](https://github.com/ryanchoi919/blog-content-pipeline), same portability idea (a project-root doc the skills read instead of hardcoding brand specifics), scoped down to a single manual drafting step instead of a full multi-gate content pipeline — maker-community posts are short-lived and low-stakes enough not to need one.
