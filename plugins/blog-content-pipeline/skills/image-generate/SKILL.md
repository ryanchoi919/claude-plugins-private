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
  2. A generation backend is actually reachable: the `COMFYUI_URL` environment variable points at a running ComfyUI server (e.g. `http://192.168.x.x:8188`), whether reached through the `comfyui` MCP server (preferred, see step 1) or by raw HTTP calls as a fallback.
- If either is missing, **do not block the pipeline**: report which one is missing, hand the approved prompts/briefs to the user as-is (for their designer or manual generation later), and move on to `draft-write` once the user acknowledges.

## Workflow files

Generation is driven by ComfyUI workflow graphs exported in **API format** (ComfyUI menu → *Save (API Format)*, not a regular workflow save), stored under `workflows/`:

- `workflows/illustration.json` — general blog illustration and Korean-text infographic backgrounds (see routing in step 3). This is a validated recipe (SDXL base 1.0 + a flat-vector-art LoRA, see `references/recommended-models.md`'s "Currently validated" section) — don't change the checkpoint/LoRA names without re-validating.
- `workflows/photographic.json` — photographic/mood feature images. Not yet authored; until it exists, treat photographic-use-case images the same as a missing backend (prompt-only handoff).

Both files use **placeholder substitution**, not node-title lookup: the positive-prompt node's `text` already contains the workflow's fixed style tags plus a `{{SCENE_PROMPT}}` placeholder, and the negative-prompt node's `text` already contains the baseline anatomy terms (mirrors `references/default-negative-prompts.md` — keep both in sync if that file changes) plus a `{{NEGATIVE_EXTRA}}` placeholder. To use a workflow file: read it as raw text, replace `{{SCENE_PROMPT}}` with this image's scene description and `{{NEGATIVE_EXTRA}}` with any constitution-specific negatives (or an empty string), JSON-escaping the substituted text first (escape `"`, `\`, and newlines) since it's being spliced into an already-quoted JSON string — then parse/submit the result. Also replace the `seed` field with a fresh random integer on every call; the checked-in value is a placeholder, not something to reuse (a fixed seed reproduces the exact same image every time).

`workflows/_template.json` is a minimal starting graph (checkpoint loader → positive/negative CLIP text encode → empty latent → sampler → VAE decode → save image) using the same placeholder convention, to duplicate when authoring `photographic.json` or a new use case. Everything else in a workflow file (sampler, scheduler, steps, cfg, LoRAs, ControlNet, custom nodes) is whatever the workflow author tuned it to — this skill never touches those fields at runtime; tune them by editing the workflow file directly and committing the change once it's validated.

## Steps

1. **Set up the connection.** Check whether a ComfyUI-flavored MCP server (tool names like `enqueue_workflow` / `get_history` / a result-fetching tool — naming varies slightly by which server is installed) is already connected in this environment. If yes, skip to step 2 — it's already configured.
   - If not connected, first get `COMFYUI_URL` — don't guess an address:
     - **Ask which connection mode applies**, since the two modes have different setup and one has a real security tradeoff:
       - *Remote* — a ComfyUI instance (e.g. ComfyUI Desktop) running on another machine on the same LAN. **ComfyUI Desktop binds to `127.0.0.1` by default and will not accept LAN connections until its listen address is changed to `0.0.0.0`** in that machine's own ComfyUI settings — a change only the user can make (on that machine), and one that exposes the ComfyUI server to the whole LAN, not just this session. Explain this plainly and get the user's explicit go-ahead before treating remote mode as configured; don't just assume the ComfyUI Desktop side is already set correctly. Once confirmed, `COMFYUI_URL` is `http://<that machine's LAN IP>:8188`.
       - *Local* — ComfyUI running on this same machine, with its own copy of the required model files (checkpoint + LoRA, several GB). `COMFYUI_URL` is `http://localhost:8188`.
     - **Resolve the actual project root first — never the current git worktree.** If this session is running inside a git worktree (e.g. under `.claude/worktrees/<name>/`), a `.claude/settings.local.json` written relative to the current directory lands in that worktree and disappears the moment the worktree is removed, silently losing the saved URL. Find the real root with `git rev-parse --git-common-dir`, which always points at the main repository's `.git` regardless of which worktree is active; the project root is that path's parent directory.
     - Read `.claude/settings.local.json` at that resolved project root (create it if missing) and merge `{"env": {"COMFYUI_URL": "<value>"}}` into it — merge into any existing `env` object, don't overwrite other keys. This value is machine-specific, so it must never go in the shared, committed `.claude/settings.json`. Confirm `.claude/settings.local.json` is listed in `.gitignore` at the project root; add it if not.
   - Then register the MCP server itself at that same project root's `.mcp.json` (create it if missing), merging in:
     ```json
     {
       "mcpServers": {
         "comfyui": {
           "command": "npx",
           "args": ["-y", "comfyui-mcp"],
           "env": { "COMFYUI_URL": "${COMFYUI_URL}" }
         }
       }
     }
     ```
     `.mcp.json` itself is safe to commit — it holds no machine-specific value, only a reference to the `COMFYUI_URL` environment variable that `.claude/settings.local.json` supplies per-machine. **Tell the user a session restart is required** for a newly-registered MCP server to actually connect — this skill cannot make it available mid-session.
   - If the MCP server still isn't reachable after setup (registration didn't take, npx/Node unavailable, etc.), fall back to raw HTTP calls against `$COMFYUI_URL` for the rest of this skill (see step 4) rather than blocking on MCP specifically.
2. For each Generated-type concept approved in `asset-metadata`, first classify its **use case** — general illustration, photographic/mood feature image, or Korean-text infographic (see routing table in step 3) — then build:
   - **Prompt** (→ `{{SCENE_PROMPT}}`): the section's illustration concept, combined with the Visual Identity section's palette/mood (the workflow file's positive-prompt node already carries the fixed style tags — e.g. "flat style vector illustration" — so this only needs to add the scene-specific and palette/mood detail, not restate the style). Default to `plain solid background, no pattern` unless the concept specifically calls for a detailed scene — abstract/conceptual words in a prompt (e.g. "streak", "series", "network") can get misread by the model as a diagram or circuit-board motif instead of the intended persona scene. For a Korean-text infographic, this covers only the background/illustration layer — never ask the model to render the Korean text or numbers themselves (see step 3).
   - **Negative prompt** (→ `{{NEGATIVE_EXTRA}}`): the Visual Identity section's "must avoid" list, minus anything already covered by the workflow file's baked-in baseline (`references/default-negative-prompts.md`'s anatomy terms — don't repeat those here, the placeholder is additive). If nothing in "must avoid" goes beyond the baseline, this can be an empty string.
   - **Dimensions**: default to a 1:1 square unless the constitution's Formatting Rules specify a different aspect ratio for in-body images.
3. **Select the workflow file for this image's use case.** Pick `workflows/illustration.json` for general illustration and Korean-infographic backgrounds, or `workflows/photographic.json` for photographic/mood images (prompt-only handoff if that file doesn't exist yet). The checkpoint and LoRA are already baked into the file as a validated pairing — don't second-guess or swap them per-request. `references/recommended-models.md` is background reading for when *authoring or updating* a workflow file, not something this skill queries live on every run.
   - **Korean-text infographics:** route to `workflows/illustration.json` for the background/illustration layer only. Never rely on the diffusion model for the Korean text/numbers themselves — composite that text afterward via HTML/SVG, outside this skill's generation call.
   - If the backend reports the checkpoint/LoRA named in the file isn't installed, or repeated OOM errors suggest a VRAM mismatch, don't silently substitute a different model — report it and fall back to a prompt-only handoff for that image (same as step 7).
4. Fill in the selected workflow (placeholder substitution, per the Workflow files section above) and submit it — **prefer the `comfyui` MCP tools when connected**, falling back to raw HTTP only if they're not:
   - **Via MCP** (e.g. `enqueue_workflow` → `get_history` → the image-fetching tool the connected server exposes, commonly `view_image`/`get_image`): pass the filled JSON to `enqueue_workflow` to get a `prompt_id`, poll `get_history` for that ID, then fetch the resulting image through the server's result tool. `get_history` on this kind of server typically surfaces full Python tracebacks on failure — read them; they're more useful for diagnosing a bad checkpoint/LoRA path or an OOM than a bare non-2xx HTTP status would be.
   - **Via raw HTTP** (fallback):
     ```
     curl -s -m 1200 -X POST "$COMFYUI_URL/prompt" \
       -H "Content-Type: application/json" \
       -d "{\"prompt\": <filled-graph-json>, \"client_id\": \"<any-uuid>\"}"
     ```
     The response contains a `prompt_id`. Poll `GET $COMFYUI_URL/history/<prompt_id>` every few seconds until that `prompt_id` appears (ComfyUI queues and executes asynchronously — the `/prompt` call returns immediately, before generation actually finishes). Once present, read the `SaveImage` node's entry under `outputs` for its `images` list (`filename`, `subfolder`, `type`), then fetch the bytes:
     ```
     curl -s -m 60 "$COMFYUI_URL/view?filename=<filename>&subfolder=<subfolder>&type=<type>" -o /tmp/gen.png
     ```
   - Either path: use a generous timeout/poll budget — **15-20 minutes**, not the default. A cold model can genuinely take that long to load on the first request, and giving up early doesn't cancel the server-side job — it just means this skill loses the result while the backend keeps working, forcing a needless retry (or worse, a queue pile-up if this happens repeatedly).
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
