#!/bin/sh
# Fires on PostToolUse for Bash commands starting with `git commit` (see hooks.json's
# `if` filter). Always reminds, since a completed Bash tool call doesn't tell us whether
# the commit itself actually succeeded, only that the tool ran.
cat <<'JSON'
{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "A `git commit` just ran. If it succeeded, check whether README/CHANGELOG/API docs need updating for what was just committed — use the doc-sync skill if so."}}
JSON
