# claude-plugins-private

ryanchoi's private Claude Code plugin marketplace. One repo, one marketplace, multiple plugins under `plugins/<name>/` — the same layout `anthropics/claude-plugins-official` uses, just private and personal.

This is the default home for a new plugin. Once something here is generally useful and safe to share, it graduates out into a public marketplace repo instead.

## Install

```
/plugin marketplace add ryanchoi919/claude-plugins-private
/plugin install <plugin-name>@ryanchoi-private
```

Private repo — Claude Code needs GitHub access to fetch it (`gh auth status`, or a `GITHUB_TOKEN` with repo read access).

## Plugins

| Plugin | Description |
|---|---|
| [`blog-content-pipeline`](plugins/blog-content-pipeline) | Constitution-driven, approval-gated content pipeline for niche blogs |
| [`community-post-kit`](plugins/community-post-kit) | Voice-driven drafting kit for maker-community posts (Disquiet, Indie Hackers, ...) with publish-status tracking |
| [`gh-issue-flow`](plugins/gh-issue-flow) | GitHub issue/PR lifecycle kit on `gh` cli: scaffold an issue, pick the next one to work on, land a PR (CI check, merge, cleanup) |

## Adding a new plugin

1. `mkdir plugins/<name>` and build it like any standalone plugin (`.claude-plugin/plugin.json` + `skills/`), just without its own `marketplace.json` — this repo's root `marketplace.json` is the only one.
2. Add an entry to the root `.claude-plugin/marketplace.json`'s `plugins` array: `{"name": "<name>", "source": "./plugins/<name>", "description": "..."}`.
3. Commit and push. Anyone with this marketplace added picks it up on `/plugin marketplace update` (or `/reload-plugins`).

## Graduating a plugin to public

Move `plugins/<name>` into the public marketplace repo's `plugins/` directory (same structure), add its entry to that repo's `marketplace.json`, remove the entry and directory here, and update anyone with an existing install to switch marketplaces.
