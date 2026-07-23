---
name: outline
description: Step 5 of the content pipeline — design the post's H1-H3 structure and FAQ set from the verified facts, and get second-gate approval. Use right after fact-enrich.
---

# Strategic Outliner

Fifth step of the content pipeline, and the **second approval gate**. Turns verified facts into a structure before any prose gets written.

## Steps

1. Using the approved plan (`idea-refine`) and verified facts (`fact-enrich`), design a full H1-H3 outline plus 3 FAQ questions.
2. Default shape (adapt to what the constitution's Mission/Voice actually call for — don't force a shape that doesn't fit the topic):
   - **H1**: the core situation + the payoff of solving it
   - **H2 Introduction**: name the reader's actual frustration before explaining anything
   - **H2 Decoding/Breakdown**: walk through the real-world mechanics (a system, a UI, an interaction) the reader will encounter
   - **H2 Essential content**: the core teachable material, in whatever mapping format the constitution specifies
   - **H2 Nuance/Etiquette notes**: the mistakes or cultural gaps the audience predictably hits
   - **H2 Quick check**: a short self-test (2-3 items) so the reader can confirm they've got it
   - **H2 Wrap-up**: key takeaways
   - **H2 FAQ**: 3 questions, in the constitution's admonition/callout syntax
3. Pick FAQ topics that add something beyond the post's main argument, not restatements of it. The body already makes the core case in full; the FAQ's job is to catch what a genuinely curious reader would ask *next* — a migration/switching detail, an edge case, a boundary condition ("does this also work for X"), a common objection or misconception, a practical follow-up action. Test each candidate: if you deleted the body and only the FAQ list remained, would this question still feel like a real, distinct thing someone wondered about the topic — or does it just re-ask the headline claim in question form so the already-written answer has somewhere to live? Cut or replace anything in the second category. A question that happens to overlap with something the body covers is fine as long as it's the natural, first thing a reader forms before choosing a specific decision (e.g. "does X have feature Y" for a head-to-head comparison) — the failure mode is an entire FAQ list where every entry just mirrors an H2's claim.
4. Write each FAQ question so it stands completely on its own — a reader must be able to understand and answer it having seen nothing else from the post (no other question, no body prose). This is the second most common way FAQ sections go wrong, so check it explicitly:
   - Never open with a connector that points at a previous question, an unnamed problem, or the body ("그럼", "이 문제", "이 방식", "that issue", "so"). Name the actual subject every time, even if it repeats a noun already used elsewhere.
   - Write it the way someone would actually type it into a search bar or ask a voice assistant — a query that could exist before this post was written — not a lead-in reverse-engineered to justify an answer you already have in mind for the body.
   - If a question only makes sense as a follow-up to the one before it (e.g. "how do you fix that?" right after a question that names the problem), that's a sign to merge the two into one self-contained question or cut one outright.
   - Read the finished FAQ list with everything else hidden: for each question, could a stranger who has never seen this post understand exactly what's being asked? If not, rewrite it.
5. Before presenting the outline, deliberately stress-test it: read through it as the target persona and look for a place where the flow breaks (a jump that assumes context the reader doesn't have yet, mismatched formality, a section that could be cut without losing anything). Fix what you find.
6. Report the outline and FAQ list to the user and **wait for explicit approval**. Do not proceed to `asset-metadata` until approved — if changes are requested, revise and re-present.
