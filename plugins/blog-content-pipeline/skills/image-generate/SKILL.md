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
  2. A generation backend is actually reachable: the `COMFYUI_URL` environment variable points at a running ComfyUI server (e.g. `http://192.168.x.x:8188`), or another image-generation MCP tool is connected in this environment.
- If either is missing, **do not block the pipeline**: report which one is missing, hand the approved prompts/briefs to the user as-is (for their designer or manual generation later), and move on to `draft-write` once the user acknowledges.

## Workflow files

Generation is driven by ComfyUI workflow graphs exported in **API format** (ComfyUI menu → *Save (API Format)*, not a regular workflow save), stored under `workflows/`:

- `workflows/illustration.json` — general blog illustration and Korean-text infographic backgrounds (see routing in step 3).
- `workflows/photographic.json` — photographic/mood feature images.

`workflows/_template.json` is a minimal starting graph (checkpoint loader → positive/negative CLIP text encode → empty latent → sampler → VAE decode → save image) to duplicate when authoring either file above. This skill locates the nodes it needs to edit by `_meta.title`, **not** by node ID (IDs get renumbered every time a graph is re-saved in the ComfyUI UI). Every workflow file must carry these titles on the relevant node:

| Title | Node (typically) | What this skill sets |
|---|---|---|
| `Checkpoint` | `CheckpointLoaderSimple` | `inputs.ckpt_name`, per the routing table in step 3 |
| `Positive Prompt` | `CLIPTextEncode` | `inputs.text` |
| `Negative Prompt` | `CLIPTextEncode` | `inputs.text` |
| `Latent Image` | `EmptyLatentImage` (or equivalent) | `inputs.width` / `inputs.height` |
| `Output` | `SaveImage` | read-only — used to find the produced file in the history response |

Everything else in the graph (sampler, scheduler, steps, cfg, LoRAs, ControlNet, custom nodes) is whatever the workflow author put there — this skill does not touch those fields. Tune them by editing the workflow file directly.

## Steps

1. Check both prerequisites above. If `COMFYUI_URL` isn't set, ask the user for it — don't guess an address. Once given, persist it so this doesn't get asked again on every run:
   - **Resolve the actual project root first — never the current git worktree.** If this session is running inside a git worktree (e.g. under `.claude/worktrees/<name>/`), a `.claude/settings.local.json` written relative to the current directory lands in that worktree and disappears the moment the worktree is removed, silently losing the saved URL. Find the real root with `git rev-parse --git-common-dir`, which always points at the main repository's `.git` regardless of which worktree is active; the project root is that path's parent directory.
   - Read `.claude/settings.local.json` at that resolved project root (create it if missing) and merge `{"env": {"COMFYUI_URL": "<value>"}}` into it — merge into any existing `env` object, don't overwrite other keys.
   - This value is machine-specific (a LAN address for one person's local backend), so it must never go in the shared, committed `.claude/settings.json`. Confirm `.claude/settings.local.json` is listed in `.gitignore` at the project root; add it if not (`.claude/settings.local.json` on its own line).
   - Tell the user it's saved and that it'll auto-load on future sessions in this project — no need to re-enter it or export it manually.
2. For each Generated-type concept approved in `asset-metadata`, first classify its **use case** — general illustration, photographic/mood feature image, or Korean-text infographic (see routing table in step 3) — then build:
   - **Prompt**: the section's illustration concept, combined with the Visual Identity section's style/palette/mood. Default to `plain solid background, no pattern` unless the concept specifically calls for a detailed scene — abstract/conceptual words in a prompt (e.g. "streak", "series", "network") can get misread by the model as a diagram or circuit-board motif instead of the intended persona scene. For a Korean-text infographic, the prompt covers only the background/illustration layer — never ask the model to render the Korean text or numbers themselves (see step 3).
   - **Negative prompt**: `references/default-negative-prompts.md`'s baseline terms merged with the Visual Identity section's "must avoid" list (dedupe overlapping terms). The baseline applies to every image regardless of what the constitution says — it exists precisely because Visual Identity sections tend to cover style/composition and never mention anatomy on their own.
   - **Dimensions**: default to a 1:1 square unless the constitution's Formatting Rules specify a different aspect ratio for in-body images.
3. **Select the workflow file for this image's use case, then route its checkpoint.**
   - Pick `workflows/illustration.json` for general illustration and Korean-infographic backgrounds, or `workflows/photographic.json` for photographic/mood images.
   - Load the file and check `GET $COMFYUI_URL/object_info/CheckpointLoaderSimple` for the checkpoints actually installed on this backend right now.
   - Match those against `references/recommended-models.md` for this image's use case (name/family match, e.g. SDXL/FLUX-family for illustration vs. FLUX.1 for photographic). If a match exists and it differs from the `Checkpoint` node's current `ckpt_name`, overwrite that field in the loaded JSON before submitting — there's no separate "switch checkpoint" call with ComfyUI; the checkpoint used is whatever the graph says when it's submitted.
   - If nothing installed matches the recommended list for this use case, leave the workflow's own `ckpt_name` as-is but tell the user generation may not match the intended style — don't block on this.
   - If the Visual Identity section calls for a non-photorealistic style (flat vector, illustration, etc.) and nothing installed matches except a realism-specialized checkpoint (e.g. a RealVisXL-style photoreal model), still prefer routing to a general-purpose or illustration-family model per the reference list — a realism checkpoint fights a flat/illustration style at the prompt level no matter how the prompt is worded.
   - **Korean-text infographics:** route to `workflows/illustration.json` for the background/illustration layer only. Never rely on the diffusion model for the Korean text/numbers themselves — no checkpoint in the reference list renders Korean glyphs reliably, so that text gets composited afterward via HTML/SVG, outside this skill's generation call.
   - If VRAM appears to be the limiting factor (repeated OOM errors, or the recommended model for this use case is known to exceed what's available), step down through `references/recommended-models.md`'s VRAM tiers one at a time — lighter quantization, then a smaller model family, then lower resolution — rather than silently changing visual style.
4. Fill in the loaded workflow JSON and submit it. Concretely: parse the JSON, walk its top-level node entries, and for each node whose `_meta.title` matches a row in the table above, set the corresponding `inputs` field (positive/negative prompt text, latent width/height, and the checkpoint name from step 3) — a short Python or Node one-liner is the reliable way to do this, not manual string edits. Then:
   ```
   curl -s -m 1200 -X POST "$COMFYUI_URL/prompt" \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": <filled-graph-json>, \"client_id\": \"<any-uuid>\"}"
   ```
   The response contains a `prompt_id`. Use a generous client-side timeout (`-m`) — **15-20 minutes**, not the default. A cold model can genuinely take that long to load on the first request, and a curl that gives up early doesn't cancel the server-side job — it just means this skill loses the result while the backend keeps working, forcing a needless retry (or worse, a queue pile-up if this happens repeatedly).
   Poll `GET $COMFYUI_URL/history/<prompt_id>` every few seconds until that `prompt_id` appears in the response (ComfyUI queues and executes asynchronously — the `/prompt` call returns immediately, before generation actually finishes). Cap total polling at the same 15-20 minute budget as above before treating it as a failure.
   Once present, read the `Output` node's entry under `outputs` in the history response for its `images` list (`filename`, `subfolder`, `type`), then fetch the actual bytes:
   ```
   curl -s -m 60 "$COMFYUI_URL/view?filename=<filename>&subfolder=<subfolder>&type=<type>" -o /tmp/gen.png
   ```
5. **Convert to WebP before saving** — never leave the final asset as PNG/JPG. Use a standalone system tool (`cwebp`/ImageMagick), not a Node package like `sharp`: this skill has to work against any target blog's stack (Hugo, Ghost, WordPress, a Node/Astro site, etc.), so the conversion step can't assume the target repo has npm or Node at all.
   ```
   cwebp -q 82 /tmp/gen.png -o <asset-path>/<filename>.webp   # preferred (libwebp)
   # or, if cwebp isn't installed:
   magick /tmp/gen.png -quality 82 <asset-path>/<filename>.webp
   ```
   Save under the project's configured asset path (from the constitution's Formatting Rules), reusing the exact filename stem already planned in `asset-metadata` but with a `.webp` extension — don't invent a different name or path. Delete the temporary PNG afterward. If neither `cwebp` nor ImageMagick is available on this machine, say so explicitly and ask the user to install one (`apt install webp` / `brew install webp`) rather than silently saving PNG.
6. **Self-screen every image before it ever reaches the user — do not skip this.** Actually view the generated file (`Read` the `.webp`), then check it against a checklist built from both the Visual Identity section's "Must avoid" list and `references/default-negative-prompts.md`'s baseline (hands, feet, limbs, proportions), item by item. This is not optional or implicit in "generation succeeded": a request returning HTTP 200 only means the backend produced *an* image, not that it honors the constitution or basic anatomy. If any item is violated (e.g. an unintended motif, a level of facial detail the Visual Identity forbids, malformed hands):
   - Revise and regenerate before showing the user anything. Keep the exact prompt text from the failed attempt and change only what caused the violation (e.g. strengthen the specific negative-prompt term tied to the violated attribute) — don't rewrite the whole prompt from scratch, and don't reference the failed image in natural language ("like image 2", "same as before"). A natural-language callback to a prior result tends to drag its entire composition/scene along with it, not just the trait you meant to fix.
   - Loop this screen-then-fix cycle until the image passes every "must avoid" item, then move on to the next concept. If it's still failing after a few honest attempts, say so and fall back to a prompt-only handoff for that image rather than looping indefinitely.
7. If a call fails (connection refused, timeout, non-2xx response) or the backend simply isn't running, don't retry in a loop — report the failure once for that image and fall back to a prompt-only handoff for it, same as when no backend is configured at all.
8. Report the self-screened images (file paths, all `.webp`) and any prompt-only fallbacks to the user and **wait for explicit approval**. On rejection, fold the user's feedback into the prompt and regenerate (same rules as step 6), or fall back to manual handoff if they'd rather not iterate. Do not proceed to `draft-write` until approved.
