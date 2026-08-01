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

1. Check both prerequisites above. If `SD_WEBUI_URL` isn't set, ask the user for it — don't guess an address. Once given, persist it so this doesn't get asked again on every run:
   - **Resolve the actual project root first — never the current git worktree.** If this session is running inside a git worktree (e.g. under `.claude/worktrees/<name>/`), a `.claude/settings.local.json` written relative to the current directory lands in that worktree and disappears the moment the worktree is removed, silently losing the saved URL. Find the real root with `git rev-parse --git-common-dir`, which always points at the main repository's `.git` regardless of which worktree is active; the project root is that path's parent directory.
   - Read `.claude/settings.local.json` at that resolved project root (create it if missing) and merge `{"env": {"SD_WEBUI_URL": "<value>"}}` into it — merge into any existing `env` object, don't overwrite other keys.
   - This value is machine-specific (a LAN address for one person's local backend), so it must never go in the shared, committed `.claude/settings.json`. Confirm `.claude/settings.local.json` is listed in `.gitignore` at the project root; add it if not (`.claude/settings.local.json` on its own line).
   - Tell the user it's saved and that it'll auto-load on future sessions in this project — no need to re-enter it or export it manually.
2. For each Generated-type concept approved in `asset-metadata`, first classify its **use case** — general illustration, photographic/mood feature image, or Korean-text infographic (see routing table in step 3) — then build:
   - **Prompt**: the section's illustration concept, combined with the Visual Identity section's style/palette/mood. Default to `plain solid background, no pattern` unless the concept specifically calls for a detailed scene — abstract/conceptual words in a prompt (e.g. "streak", "series", "network") can get misread by the model as a diagram or circuit-board motif instead of the intended persona scene. For a Korean-text infographic, the prompt covers only the background/illustration layer — never ask the model to render the Korean text or numbers themselves (see step 3).
   - **Negative prompt**: the Visual Identity section's "must avoid" list.
   - **Dimensions**: default to a 1:1 square unless the constitution's Formatting Rules specify a different aspect ratio for in-body images.
3. **Route to the right checkpoint before generating, if the backend has more than one loaded.** Check `GET $SD_WEBUI_URL/sdapi/v1/sd-models` for what's available and `GET $SD_WEBUI_URL/sdapi/v1/options` for what's currently active.
   - Match the available models against `references/recommended-models.md` for this image's use case (name/family match, e.g. SDXL/FLUX-family for illustration vs. FLUX.1 for photographic). If a match exists and it differs from the active checkpoint, switch to it.
   - If nothing on the backend matches the recommended list for this use case, keep the currently active checkpoint but tell the user generation may not match the intended style — don't block on this.
   - If the Visual Identity section calls for a non-photorealistic style (flat vector, illustration, etc.) and the only available/active checkpoint is realism-specialized (e.g. a RealVisXL-style photoreal model), still prefer switching to a general-purpose or illustration-family model per the reference list — a realism checkpoint fights a flat/illustration style at the prompt level no matter how the prompt is worded.
   - **Korean-text infographics:** route to the same model family as general illustration for the background/illustration layer only. Never rely on the diffusion model for the Korean text/numbers themselves — every checkpoint in the reference list renders Korean glyphs unreliably, so that text gets composited afterward via HTML/SVG, outside this skill's generation call.
   - If VRAM appears to be the limiting factor (repeated OOM errors, or the recommended model for this use case is known to exceed what's available), step down through `references/recommended-models.md`'s VRAM tiers one at a time — lighter quantization, then a smaller model family, then lower resolution — rather than silently changing visual style.
   - Switch checkpoints via `POST $SD_WEBUI_URL/sdapi/v1/options -d '{"sd_model_checkpoint": "<name>"}'`. Do this as its own call, separate from the generation request below — a checkpoint switch reloads the model and can itself take minutes, and bundling it into the same timing budget as generation is how requests appear to hang.
4. Call the backend. For an AUTOMATIC1111-style API:
   ```
   curl -s -m 1200 -X POST "$SD_WEBUI_URL/sdapi/v1/txt2img" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "...", "negative_prompt": "...", "steps": 25, "cfg_scale": 7, "width": 1024, "height": 1024, "save_images": true}'
   ```
   Use a generous client-side timeout (`-m`) — **15-20 minutes**, not the default. A cold model (or one that just finished a checkpoint switch) can genuinely take that long on the first request, and a curl that gives up early doesn't cancel the server-side job — it just means this skill loses the result while the backend keeps working, forcing a needless retry (or worse, a queue pile-up if this happens repeatedly).
   `save_images: true` matters: A1111's API only returns base64 by default and does **not** write anything to disk on the backend machine unless this is set — without it, a failed transfer or a skill bug loses the generation entirely, with no copy anywhere to recover from. Setting it gives the backend machine's own `outputs/txt2img-images/` a persistent audit trail independent of whatever this skill does with the response.
   Decode the returned base64 image(s) to a temporary PNG.
5. **Convert to WebP before saving** — never leave the final asset as PNG/JPG. Use a standalone system tool (`cwebp`/ImageMagick), not a Node package like `sharp`: this skill has to work against any target blog's stack (Hugo, Ghost, WordPress, a Node/Astro site, etc.), so the conversion step can't assume the target repo has npm or Node at all.
   ```
   cwebp -q 82 /tmp/gen.png -o <asset-path>/<filename>.webp   # preferred (libwebp)
   # or, if cwebp isn't installed:
   magick /tmp/gen.png -quality 82 <asset-path>/<filename>.webp
   ```
   Save under the project's configured asset path (from the constitution's Formatting Rules), reusing the exact filename stem already planned in `asset-metadata` but with a `.webp` extension — don't invent a different name or path. Delete the temporary PNG afterward. If neither `cwebp` nor ImageMagick is available on this machine, say so explicitly and ask the user to install one (`apt install webp` / `brew install webp`) rather than silently saving PNG.
6. **Self-screen every image before it ever reaches the user — do not skip this.** Actually view the generated file (`Read` the `.webp`), then check it against a checklist built directly from the Visual Identity section's "Must avoid" list, item by item. This is not optional or implicit in "generation succeeded": a request returning HTTP 200 only means the backend produced *an* image, not that it honors the constitution. If any item is violated (e.g. an unintended motif, a level of facial detail the Visual Identity forbids):
   - Revise and regenerate before showing the user anything. Keep the exact prompt text from the failed attempt and change only what caused the violation (e.g. strengthen the specific negative-prompt term tied to the violated attribute) — don't rewrite the whole prompt from scratch, and don't reference the failed image in natural language ("like image 2", "same as before"). A natural-language callback to a prior result tends to drag its entire composition/scene along with it, not just the trait you meant to fix.
   - Loop this screen-then-fix cycle until the image passes every "must avoid" item, then move on to the next concept. If it's still failing after a few honest attempts, say so and fall back to a prompt-only handoff for that image rather than looping indefinitely.
7. If a call fails (connection refused, timeout, non-2xx response) or the backend simply isn't running, don't retry in a loop — report the failure once for that image and fall back to a prompt-only handoff for it, same as when no backend is configured at all.
8. Report the self-screened images (file paths, all `.webp`) and any prompt-only fallbacks to the user and **wait for explicit approval**. On rejection, fold the user's feedback into the prompt and regenerate (same rules as step 6), or fall back to manual handoff if they'd rather not iterate. Do not proceed to `draft-write` until approved.
