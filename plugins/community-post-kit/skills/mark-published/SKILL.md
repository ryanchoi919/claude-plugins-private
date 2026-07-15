---
name: mark-published
description: Given the live URL of a maker-community post, find the matching saved draft under marketing/community-posts/posts/ and flip its YAML frontmatter status from draft to published, recording the URL. Use after the user has manually posted something the `post` skill drafted, to keep the saved file's bookkeeping in sync with reality.
---

# Mark Published

Records that a previously-drafted post has actually gone live. This skill never publishes anything itself — it only updates bookkeeping (`status`, `url`, `published_at`) on a file `post` already saved, after the user pastes back the live URL.

## Prerequisite

At least one file must already exist under `marketing/community-posts/posts/<platform>/`. If the directory doesn't exist at all, tell the user there's nothing to mark yet and stop — direct them to `post` first.

## When invoked

1. **Identify the platform from the URL's host.** Read each platform section's `URL domain` field in `marketing/community-posts/VOICE.md` and match it against the given URL's domain.
   - If no `URL domain` matches (or VOICE.md hasn't been filled in with one), ask the user which platform this URL belongs to instead of guessing.
2. **Find the candidate file(s).** List files under `marketing/community-posts/posts/<platform>/` whose frontmatter `status` is not already `published`, sorted by `created` descending.
   - Exactly one candidate: confirm it with the user by summarizing its slug and topic before changing anything — don't update silently.
   - Multiple candidates: list each (slug, created date, first line of the body) and ask which one this URL corresponds to.
   - None found (every file for that platform is already `published`, or the folder is empty): say so, and ask whether this is a post that was never drafted through `post` — if so, don't fabricate a new file here; point the user at `post` instead.
3. **Update the confirmed file's frontmatter only:**
   - `status: published`
   - `url: <the given URL>`
   - `published_at: <today's date, YYYY-MM-DD>`

   Leave the post body untouched.
4. Report exactly what changed — file path, old status → new status, URL set — and stop.

## Rules

- Never guess which file matches when more than one candidate is plausible. Silently updating the wrong post's status is worse than pausing to ask.
- Touch frontmatter only; never edit the post body while marking it published.
- If the matched file already has `status: published` with a *different* URL already set, flag the conflict to the user instead of silently overwriting it — it usually means two posts are being confused with each other.
