---
name: draft-write
description: Step 7 of the content pipeline — write the full post draft in the project's voice, using its custom components and formatting rules, then get fourth-gate approval. Use right after asset-metadata.
---

# Draft Writer & Humanizer

Seventh step of the content pipeline, and the **fourth approval gate**. Produces the actual post body.

## Steps

1. Write the full draft at the project's content path (e.g. `content/posts/{category}/{slug}/index.md` — adjust to whatever the constitution's Formatting Rules specify), following the approved outline, metadata, and asset placements exactly.
2. If the constitution's Formatting Rules define a multi-language mapping format (e.g., native text + romanization + translation), apply it to every instance of the taught language content, each element on its own line, exactly as specified — no exceptions and no shortcuts.
3. Insert image placeholders exactly where planned in `asset-metadata`, whenever a section runs long (roughly 7-10+ lines) without a visual break, or wherever an asset was approved:
   - Standalone markdown image syntax only — never inside a callout/admonition block.
   - Format: `![<type icon/label>: <filename> (<what it shows / prompt concept>)](<filename>)`
4. Use the constitution's custom components/shortcodes exactly as specified (name, arguments, casing) — do not invent new ones and do not skip required ones (e.g. a category badge, a phrase/vocab card, a source citation block, a lead-magnet CTA at the end).
5. Follow the constitution's admonition/callout syntax exactly, including any forbidden syntax that would break the build. Pay special attention to any documented gotcha (e.g. a required trailing character on collapsible FAQ blocks, no bold text in callout titles).
6. **Humanize the tone**: reread the full draft and strip any dry, explainer-AI phrasing ("This system is...", "There is a rule that..."). Rewrite in the exact persona from the constitution's Voice & Tone section — the goal is that a reader can tell a specific kind of person wrote this, not a generic assistant.
7. If the constitution defines a minimum length/depth or an internal-linking requirement, meet it in this draft rather than leaving it for `seo-vet` to catch — pad-free depth (a genuinely new angle per section, not the same point restated) and real links to existing published content, not placeholders.
8. Give the draft an actual ending, not just a stop. If the constitution bans cliché wrap-up phrasing, honor that by avoiding the phrasing — not by dropping the closing thought. The last paragraph should still do one of: answer the question/scene the piece opened with, hand the reader a concrete next step, or resolve the open choice the piece was building toward.
9. Report the completed draft (or a tight summary of it, if very long) to the user and **wait for explicit approval**. Do not proceed to `seo-vet` until approved — if changes are requested, revise and re-present.
