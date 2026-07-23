---
name: land-pr
description: Check CI status on an open GitHub PR and, once every check is green, merge it and clean up the local branch/worktree used for it. Use when the user asks to land, merge-when-green, or wrap up a PR (e.g. "ci 통과되면 머지해줘", "이 PR 랜드해줘", "머지되면 정리해줘").
---

# Land PR

Takes a PR from "CI running" to "merged and cleaned up" in one flow: waits on checks, merges once green, then removes the branch and local worktree.

## When invoked

1. **Identify the PR.** If the current directory/worktree is on a branch with an associated PR, use `gh pr view` to resolve it. If ambiguous (not on a PR branch, or the user names a different PR/number), ask.
2. **Check CI status.** Run `gh pr checks <number>`.
   - If any check is failing, report which one(s) and stop — do not merge, and do not silently retry.
   - If checks are still pending and the user's request implied waiting ("CI 통과되면 머지해줘"), poll on a reasonable interval (e.g. every 30–60s) up to a sane timeout, reporting status changes rather than going silent. If the user asked to check status only, report the current state once and stop.
3. **Confirm merge method** the first time in a repo: check `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed,deleteBranchOnMerge` and ask the user's preference if more than one method is allowed and none has been established in this conversation. Reuse that preference for subsequent calls in the same session instead of re-asking every time.
4. **Merge.** Once green, run `gh pr merge <number> --<method> --delete-branch` (squash/merge/rebase per the resolved method). This is a merge to a shared branch — if the user's original request didn't already give explicit go-ahead to merge automatically once green, confirm right before merging rather than assuming silence means yes.
5. **Clean up locally.** If the current session is working out of a worktree for this branch, exit and remove it (`ExitWorktree` if available in this session, otherwise `git worktree remove`) after the merge succeeds — never before, in case the merge fails.
6. **Report** the merged PR URL and what was cleaned up (branch deleted remotely, worktree removed locally).

## Rules

- Never merge with failing or pending checks, and never force-merge past branch protection.
- Don't delete the worktree/branch until the merge has actually succeeded — a failed merge should leave the working state untouched so the user can retry.
- If the repo has no CI checks configured at all, say so explicitly rather than treating "no checks" the same as "checks passed."
