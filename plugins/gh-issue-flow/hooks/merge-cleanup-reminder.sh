#!/bin/sh
# Fires on PostToolUse for Bash commands starting with `gh pr merge` (see hooks.json's
# `if` filter) — i.e. only when a PR is merged directly, bypassing the merge-pr skill's
# own cleanup step (SKILL.md step 5). Always reminds, since a completed Bash tool call
# doesn't tell us the shell command's own exit code, only that the tool itself ran.
cat <<'JSON'
{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "A `gh pr merge` just ran directly via Bash, not through the gh-issue-flow merge-pr skill. If it succeeded, check whether the merged branch still has a local git worktree/branch that needs cleaning up."}}
JSON
