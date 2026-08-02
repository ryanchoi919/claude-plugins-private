# Recommended models for local generation

Reference list for `image-generate`'s model-routing step. Kept out of `SKILL.md` on purpose: the local model ecosystem shifts faster than the skill's routing logic should have to, so this file is the thing to edit when a new model family becomes the better default — not the skill body.

## How this is used

1. `image-generate` queries `GET $COMFYUI_URL/object_info/CheckpointLoaderSimple` for what's actually installed on this backend right now.
2. It matches the returned `ckpt_name` enum values against the **Name patterns** column below (case-insensitive substring match) for the current image's use case.
3. First match wins, and the matched name is written into the selected workflow file's `Checkpoint` node before submission (see `SKILL.md`'s Workflow files section). If nothing matches, fall back to whatever `ckpt_name` the workflow file already has and tell the user generation may not match the intended style.

## By use case

| Use case | Preferred family | Name patterns to match | VRAM floor |
|---|---|---|---|
| General blog illustration (flat/vector, non-photoreal) | SDXL-based illustration checkpoint, or FLUX.2 Klein 4B (quantized) | `sdxl`, `illustri`, `flux.2.*klein`, `flux.*schnell` | 8GB (SDXL) / 12GB (FLUX small) |
| Photographic / mood-driven feature image | FLUX.1 (dev or schnell) | `flux.1`, `flux-dev`, `flux-schnell` | 12GB+ |
| Korean-text infographic — background/illustration layer only | same as general illustration | same as above | 8GB+ |

**Korean-text infographics never get their text from the diffusion model.** No checkpoint in this list renders Korean glyphs reliably — this is a model-family limitation, not a quality gap a better prompt fixes. Generate only the background/illustration through the matched model above; composite the actual Korean text and numbers separately via HTML/SVG. Treat this as a hard rule in the routing logic, not a fallback for low-quality output.

## VRAM tiers

Informational, from `nvidia-smi --query-gpu=name,memory.total,power.limit --format=csv`.

| VRAM | Usable | If the preferred model for a use case doesn't fit |
|---:|---|---|
| 4GB | SD 1.5 only, low resolution | drop to SD 1.5; tell the user quality will be visibly lower |
| 6GB | SDXL (optimized), 1024px single image | drop resolution before dropping model family |
| 8GB | SDXL, some FLUX quantized, LoRA | recommended floor |
| 12GB | FLUX small, ControlNet, upscaling | recommended |
| 16GB+ | multi-model workflows, high resolution | comfortable |
| 24GB+ | large models, training/fine-tuning, batch generation | professional |

VRAM limits *which options are available* (model size, quantization, resolution, batch size) — it does not limit quality at a fixed configuration. The same model/resolution/sampler/steps/precision produces the same result on 8GB and 24GB. When the preferred model for a use case doesn't fit, step down one row at a time — lighter quantization, then a smaller model family, then lower resolution — rather than silently switching to a different visual style.

## External fallback (quality-critical only)

If a specific image genuinely needs quality no local backend can reach, fall back to an external API (OpenAI/Gemini/BFL) instead of forcing an undersized local model — but only when the constitution or the user explicitly calls for it. This path has cost/ToS implications the local path doesn't, so don't reach for it as a default.
