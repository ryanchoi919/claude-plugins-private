---
name: image-generate
description: Step 7 of the content pipeline — generate the in-body illustrations approved in asset-metadata, using a configured local image-generation backend and the constitution's Visual Identity section, then get fourth-gate approval. Use right after asset-metadata. Skip entirely if the constitution has no Visual Identity section or no backend is configured.
---

# Image Generator

Seventh step of the content pipeline, and the **fourth approval gate**. Generates the "Generated-type" illustrations that `asset-metadata` proposed but deliberately did not create.

## When this applies

- Only for concepts `asset-metadata` marked **Generated-type** (illustrations, scene depictions) — never for diagram/capture-type assets (screenshots, maps, structured reference visuals), and never for the post's main/featured thumbnail (out of scope here — see `asset-metadata`).
- Requires both of the following to be true:
  1. `CONSTITUTION.md` has a filled-in **Visual Identity** section — not missing, not "Not used.", not the raw template placeholder.
  2. A generation backend is actually reachable: either the `SD_WEBUI_URL` environment variable points at a running AUTOMATIC1111-compatible WebUI (e.g. `http://192.168.x.x:7860`), or another image-generation MCP tool is connected in this environment.
- If either is missing, **do not block the pipeline**: report which one is missing, hand the approved prompts/briefs to the user as-is (for their designer or manual generation later), and move on to `draft-write` once the user acknowledges.

## Steps

1. Check both prerequisites above. If `SD_WEBUI_URL` isn't set but the user has mentioned a backend exists, ask once for the URL for this session — don't guess an address.
2. For each Generated-type concept approved in `asset-metadata`, build:
   - **Prompt**: the section's illustration concept, combined with the Visual Identity section's style/palette/mood.
   - **Negative prompt**: the Visual Identity section's "must avoid" list.
   - **Dimensions**: default to a 1:1 square unless the constitution's Formatting Rules specify a different aspect ratio for in-body images.
3. Call the backend. For an AUTOMATIC1111-style API:
   ```
   curl -s -X POST "$SD_WEBUI_URL/sdapi/v1/txt2img" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "...", "negative_prompt": "...", "steps": 25, "cfg_scale": 7, "width": 1024, "height": 1024}'
   ```
   Decode the returned base64 image(s) and save under the project's configured asset path (from the constitution's Formatting Rules), using the exact filename already planned in `asset-metadata` — don't invent a different name or path.
4. If a call fails (connection refused, timeout, non-2xx response) or the backend simply isn't running, don't retry in a loop — report the failure once for that image and fall back to a prompt-only handoff for it, same as when no backend is configured at all.
5. Report the generated images (file paths) and any prompt-only fallbacks to the user and **wait for explicit approval**. On rejection, fold the user's feedback into the prompt and regenerate, or fall back to manual handoff if they'd rather not iterate. Do not proceed to `draft-write` until approved.
