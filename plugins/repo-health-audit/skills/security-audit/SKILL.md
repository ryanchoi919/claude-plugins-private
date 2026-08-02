---
name: security-audit
description: Full-repository (not diff-scoped) security audit — scans the whole codebase for auth/authz gaps, injection, hardcoded secrets, unsafe deserialization, and missing input validation, and reports only P0/P1 findings per the shared severity rubric. Use for a repo-wide security health check, not for reviewing a specific PR/diff (use the built-in /security-review for that). Triggers on requests like "보안 관점에서 전체 코드베이스 점검해줘", "security audit 돌려줘", "보안 취약점 전수 조사".
---

# Security Audit

Scans the **entire repository**, not a diff — finds latent security issues that were never caught by any PR review because they were never part of a reviewed change. Complements (does not replace) diff-scoped review tools.

## When invoked

1. **Read the severity rubric** at `${CLAUDE_PLUGIN_ROOT}/reference/severity-rubric.md` before classifying anything.
2. **Learn the repo's own security posture first**, so this pass doesn't re-flag what's already handled:
   - Look for an existing security policy doc (e.g. `docs/SECURITY_AUDIT_POLICY.md` or similar) and any dependency-vulnerability CI gate (e.g. an `audit:ci`-style script, Dependabot config, `npm audit` in CI). If a gate already covers a category (e.g. known-CVE dependency scanning), don't re-report what it already catches — focus on what static/manual review adds.
   - Note the repo's stack (frameworks, auth provider, DB client) from `package.json`/`CLAUDE.md`/`AGENTS.md` so checks are relevant instead of generic.
3. **Scan systematically** across the whole tree (respecting `.gitignore`; skip generated/vendored/lockfile content). Look for, at minimum:
   - Auth/authz gaps: endpoints or mutations missing an auth check that sibling endpoints have; client-side-only authorization; privilege checks that trust client-supplied data.
   - Injection: string-concatenated SQL/shell/HTML from untrusted input; unsafe `eval`/dynamic `require`/template injection.
   - Secrets: hardcoded API keys/tokens/passwords/connection strings in source (not `.env.example` placeholders).
   - Unsafe deserialization / unsafe use of `pickle`-equivalents, `yaml.load` without safe loader, etc.
   - Missing input validation at trust boundaries (user input, webhook payloads, file uploads).
4. **Classify** each candidate against the rubric. Discard P2/P3 outright — do not include them in the report body, just note a discard count.
5. **Report** a structured list of P0/P1 findings only, each as:
   ```
   - severity: P0|P1
     title: <short, specific>
     file: <path>
     line: <line or range>
     evidence: <the actual risky code/pattern, quoted briefly>
     why_it_matters: <concrete exploit/impact scenario, not a generic OWASP label>
     suggested_fix: <what would actually resolve it>
   ```
6. This skill only **reports** findings — it does not create issues or PRs itself. `run-audit` (or a human) decides what to do with the report.

## Rules

- Never invent a finding to have something to report — a clean pass with zero P0/P1 is a valid, good outcome. State it plainly.
- Don't duplicate what the repo's own CI security gate already enforces (e.g. a dependency-vulnerability allowlist policy) — call out gaps in *coverage* of that gate instead, if any.
- Evidence must be real, cited file:line — never a paraphrase you can't point to in the tree.
