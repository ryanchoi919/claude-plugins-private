---
name: scaffold-issue
description: Turn a rough bug report, feature idea, or pasted error/log into a well-formed GitHub issue via gh cli — proper title, structured body, and labels matched to the repo's existing label set — after checking for likely duplicates. Use when the user describes a problem or idea and asks to file/create/register it as an issue (e.g. "이슈로 등록해줘", "버그 이슈 만들어줘", "이거 이슈 하나 파줘").
---

# Scaffold Issue

Converts a free-form description (prose, pasted stack trace, screenshot description, or a short idea) into a properly structured GitHub issue in the target repo, using `gh issue create`.

## When invoked

1. **Get the raw material.** Use whatever the user already gave in the same message (description, log, error text). If it's too thin to act on (e.g. just "버그 있음"), ask one or two targeted follow-up questions (repro steps, expected vs actual, where it was seen) rather than guessing.
2. **Resolve the target repo.** If the current directory is inside a git repo with a GitHub remote, use that. If it's ambiguous (no repo, or the user's wording suggests a different repo than the cwd), ask which repo before doing anything else.
3. **Check for duplicates.** Run `gh issue list --search "<key terms>" --state all --limit 10` (or similar) and skim titles/bodies. If a clear duplicate or closely related open issue exists, surface it and ask whether to comment there instead of filing a new one — don't silently create a duplicate.
4. **Match the repo's conventions.**
   - If `.github/ISSUE_TEMPLATE/` exists, follow its structure/sections for the body instead of inventing your own format.
   - Run `gh label list` and pick from existing labels (e.g. bug/enhancement/refactor/docs) based on fit — don't invent new labels or leave labeling to guesswork if nothing fits well; it's fine to create the issue with no label rather than a wrong one.
5. **Draft.** Write a concise, specific title (not a restatement of the raw input) and a body covering, as applicable: context/what happened, repro steps, expected vs actual, and any relevant links/files/logs the user provided.
6. **Approval gate.** Show the drafted title, body, and chosen label(s) and ask for confirmation or edits. Do not call `gh issue create` before approval.
7. **Create.** Run `gh issue create --title "..." --body "..." --label "..."`, then report the resulting issue number and URL.

## Rules

- Never assign the issue, set a milestone, or add it to a project board unless the user explicitly asks — scope is title/body/labels only.
- If duplicate-checking turns up nothing conclusive (e.g. `gh issue list --search` unsupported or the repo has too many issues to skim usefully), say so rather than silently skipping the check.
- Keep the body proportional to the input — a two-line bug report shouldn't be inflated into a template with empty sections.
