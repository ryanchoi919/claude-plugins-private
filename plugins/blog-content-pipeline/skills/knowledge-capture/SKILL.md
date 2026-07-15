---
name: knowledge-capture
description: File a reusable, domain-general fact, nuance, or methodology into this project's knowledge base, cross-linked with existing entries. Use when seo-vet flags something reusable, or any time research surfaces a fact worth keeping beyond the current post.
---

# Knowledge Capture

Turns a fragment of research into a permanent, cross-linked asset in the project's knowledge base, so future posts can treat it as a trusted source instead of re-researching it from scratch.

Only applies if `CONSTITUTION.md`'s Knowledge Base section defines a path and categories. If it says "Not used," this skill doesn't apply to this project.

## Principles

- **Cost efficiency**: prefer fetching one authoritative page directly (`WebFetch`) over repeated broad searches when verifying a specific claim.
- **Objectivity**: write knowledge-base entries in a dry, factual register — this is a reference source, not a blog post. Save the brand voice for the posts that cite it.
- **Cross-linking**: no entry should be an island. Always look for related existing entries and link both ways.

## Steps

1. **Research**: gather the background needed to state the fact/rule/methodology precisely and correctly, with sources. Use a research MCP tool if connected, otherwise `WebSearch` + `WebFetch`. Keep a list of every source URL cited.
2. **Classify**: pick the right category from `CONSTITUTION.md`'s Knowledge Base categories. Draft an H2/H3 structure and a short `summary` + `tags` for the frontmatter.
3. **Verify**: for each cited URL, actually fetch it (`WebFetch`) and confirm it says what you claim it says. Assign a `confidence` rating (`high`/`medium`/`low`) based on how directly the source supports the claim.
4. **Raw preservation (optional)**: if a source is unusually authoritative and likely to be cited repeatedly (an official standards body, a foundational paper), ask the user whether to preserve the full original text as a permanent file under `knowledge/raw/<source>/<YYYYMMDD>_<title>.md`. Only do this with explicit approval.
5. **Cross-link**: search the existing knowledge base for entries related by topic or tag. Add a `## Related` section linking to them, and update those existing entries to link back to the new one.
6. **Save**: write the entry to `<knowledge base path>/<category>/<slug>.md` following whatever frontmatter schema `knowledge/README.md` (or equivalent) defines for that project — at minimum `title`, `category`, `created_at`, `source`, `original_url`, `tags`, `summary`, `confidence`.
7. Report back what was filed and how many entries were cross-linked.
