---
name: seo-vet
description: Step 8 (final) of the content pipeline — vet the draft against every constitution rule and SEO basics, offer to capture any reusable new knowledge, and get final publish approval. Use right after draft-write.
---

# SEO & Brand Vetting

Eighth and final step of the content pipeline, and the **fifth (final) approval gate**.

## Steps

1. Run through this checklist against the approved draft and metadata, and fix anything that fails before reporting:
   - **Brand fit**: does the tone actually match `CONSTITUTION.md`'s Voice & Tone, all the way through — not just the intro?
   - **Keyword placement**: does the target keyword from `idea-refine` show up naturally in the meta description, at least one H2/H3, and the body?
   - **Frontmatter**: every required field from the constitution present, correctly typed, category value valid, thumbnail filename matches what was actually planned?
   - **Custom components**: every shortcode/component used has correctly closed, correctly cased arguments?
   - **Mapping format**: if the constitution defines a multi-language or structured mapping format, does every instance in the body follow it with no exceptions?
   - **Admonition/FAQ syntax**: matches the constitution exactly, including any documented gotcha (trailing characters, forbidden bold, forbidden shortcodes)?
   - **Asset paths**: do image placeholders point to paths consistent with the project's content structure?
2. **Knowledge capture offer**: if this post's research surfaced any fact, nuance, or methodology that's genuinely reusable beyond this one post (and the constitution defines a knowledge base), offer to run the `knowledge-capture` skill now to file it away before publishing. Don't force this — skip if nothing reusable came up, or if the constitution says "Not used" for its knowledge base.
3. Report the vetting results (what was checked, what if anything was fixed) to the user and **wait for explicit final publish approval**. This closes the pipeline — actually committing/publishing the file is a separate, explicit action the user takes or asks for after this approval.
