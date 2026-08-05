---
name: asset-metadata
description: Step 6 of the content pipeline — plan visual assets and finalize frontmatter/metadata for the approved outline, then get third-gate approval. Use right after outline.
---

# Asset & Meta Planner

Sixth step of the content pipeline, and the **third approval gate**.

## Steps

1. **Asset planning**: for each section of the approved outline, decide where an image would help and what kind:
   - Diagram/capture-type: screenshots, maps, structured reference visuals — for a third-party source (e.g. an official blog/press image), note the source URL if already known so `image-generate` doesn't have to ask twice.
   - Generated-type: illustrations, scene depictions
   - Never generate or fetch images at this stage. Propose the concept/prompt (Generated-type) or the source/reference (Diagram/capture-type) for each and wait for approval — actual production happens in `image-generate` (the next step). Generated-type only proceeds there if the constitution's Visual Identity section is filled in and a generation backend is configured; Diagram/capture-type only proceeds there if a usable source can be found and its reuse rights are clear. Whichever condition isn't met, the brief goes to the user's designer instead.
   - The post's main/featured thumbnail is out of scope for asset planning if the constitution says thumbnails are hand-made — only propose the *filename* to reference in frontmatter, never the image itself.
   - If the constitution's Visual Identity section is filled in, follow it exactly for any generated-image prompts.
2. **Metadata**: draft the frontmatter using the exact schema from `CONSTITUTION.md`'s Formatting Rules — every required field, in the required format. Do not add fields the constitution doesn't list (e.g. platform-specific fields from a different CMS).
3. Report the asset placement list and the draft frontmatter to the user and **wait for explicit approval**. Do not proceed to `draft-write` until approved.
