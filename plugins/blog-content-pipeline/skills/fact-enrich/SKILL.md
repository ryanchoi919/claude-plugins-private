---
name: fact-enrich
description: Step 4 of the content pipeline — verify and enrich the approved plan with accurate, sourced facts, cross-checked against the project's knowledge base. Use only after idea-refine has been explicitly approved by the user.
---

# Fact Enricher

Fourth step of the content pipeline. Runs only after the user has approved the plan from `idea-refine`. Turns the approved plan into verified, citable facts.

## Steps

1. Check the project's knowledge base first, if `CONSTITUTION.md` defines one (Knowledge Base section). Search it (`Grep`/file search) for anything already covering this topic — treat existing knowledge-base entries as higher-trust than a fresh web search.
2. Research whatever facts the plan still needs: authoritative standards/rules, real-world phrasing or behavior (not just the textbook version), common misconceptions the audience has, and precise translations/equivalents if the constitution's Formatting Rules include a multi-language mapping format.
   - Use a Perplexity/research MCP tool if connected, otherwise `WebSearch` + `WebFetch`.
   - Cost-control rule: compose **one** comprehensive query rather than several small ones.
3. Cross-check any uploaded source material (`sources/` folder from `idea-refine`) against what research turns up. When they conflict, the uploaded source material wins — it's the project's own ground truth. Note the conflict and resolution explicitly (e.g., "general web sources say X, but the uploaded reference says Y because of Z — going with Y").
4. If the post format benefits from it, also produce: comparison-table data, and situation-based example scripts/scenarios the reader can directly reuse.
5. Do not report back yet — hold the verified facts in context and proceed directly to `outline`. No user approval needed at this stage (verification happens implicitly via the outline and draft approval gates).
