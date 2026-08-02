# Default negative prompts

Baseline negative-prompt terms for `image-generate`, applied to **every** generation regardless of what the constitution's Visual Identity section says. Kept out of `SKILL.md` for the same reason as `recommended-models.md`: this is a list to tune from real generation failures, not skill logic.

Merge these with the Visual Identity section's "must avoid" list (dedupe overlapping terms) before writing the `Negative Prompt` node. Never drop the baseline even if a Visual Identity section defines its own negative list — that list is written by someone thinking about style and composition, not anatomy, and won't cover this on its own.

## Anatomy (hands, feet, limbs)

```
bad anatomy, malformed hands, poorly drawn hands, extra fingers, fused fingers, mutated hands, missing fingers, extra limbs, missing limbs, disproportionate body, distorted proportions, twisted limbs, malformed feet, poorly drawn feet, deformed
```

This category exists because a real generation batch (SDXL base 1.0, DPM++ 2M Karras, steps 22, cfg 7.0) produced visibly malformed hands — overlapping fingers, a phantom extra hand, awkward crossed legs — while the negative prompt in use at the time covered text/logo/color/composition but had zero anatomy terms. Diagnosis confirmed the missing negative terms as the primary cause, ahead of switching models or reaching for a LoRA.

## Known failure mode: CFG interaction

Flat/vector or otherwise simplified illustration styles are more prone to hand/limb distortion at higher CFG (7 and up) — the model has less real anatomical detail to fall back on in that style, so ambiguous regions like hands warp more easily as guidance strength increases. If malformed-hand issues persist after adding the terms above, lowering `cfg` to 5–6 in the workflow's `Sampler` node is the next thing to try before reaching for a LoRA or hand/face detailer node.

A "flat design/vector art" LoRA can help overall style consistency, but it does not directly fix anatomy collapse — treat the negative prompt (and CFG, if needed) as the fix, and a LoRA as a separate, later style decision.
