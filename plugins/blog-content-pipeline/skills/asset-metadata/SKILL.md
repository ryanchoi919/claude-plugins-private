---
name: asset-metadata
description: Step 6 of the content pipeline — plan visual assets and finalize frontmatter/metadata for the approved outline, then get third-gate approval. Use right after outline.
---

# Asset & Meta Planner

Sixth step of the content pipeline, and the **third approval gate**.

## Steps

1. **Asset planning**: for each section of the approved outline, decide where an image would help and what kind:
   - Diagram/capture-type: screenshots, maps, structured reference visuals
   - Generated-type: illustrations, scene depictions
   - Never generate images at this stage. Propose the concept/prompt for each and wait for approval before any generation tool is invoked (in a later step, and only if an image-generation tool/MCP is actually connected in this environment — otherwise hand the brief to the user's designer instead).
   - The post's main/featured thumbnail is out of scope for asset planning if the constitution says thumbnails are hand-made — only propose the *filename* to reference in frontmatter, never the image itself.
   - If the constitution defines an illustration style guide (palette, style, what to avoid), follow it exactly for any generated-image prompts.
2. **Metadata**: draft the frontmatter using the exact schema from `CONSTITUTION.md`'s Formatting Rules — every required field, in the required format. Do not add fields the constitution doesn't list (e.g. platform-specific fields from a different CMS).
3. Report the asset placement list and the draft frontmatter to the user and **wait for explicit approval**. Do not proceed to `draft-write` until approved.
