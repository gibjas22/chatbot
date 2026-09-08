---
name: ogenic-ship
description: "Commit, branch, pull request and release discipline for the Ogenic toolkit. Use when Gibson asks to commit, push, open a PR, merge, tag or release, and as the final stage of ogenic-code-workflow. Covers commit granularity, message format, the pre-push gate, PR bodies and rollback."
---

# Ogenic Ship

Shipping is a discipline, not a keystroke. The gate below runs before every push, without exception.

## Branches

- Never commit directly to `main`. Branch first, always.
- One branch, one purpose. If the branch name needs "and", it is two branches.
- Naming: `<type>/<short-kebab-summary>`, where type is `feat`, `fix`, `chore`, `docs`, `refactor` or `test`.
- Branch from an up-to-date base: `git fetch origin main && git checkout -b feat/thing origin/main`.

## Commits

### Granularity

One commit, one logical change. A reviewer should be able to read a commit, understand it, and accept or reject it on its own.

- Split formatting from behaviour. A rename mixed into a logic change hides the logic change.
- A commit should leave the tree working. If step 2 needs step 3 to compile, they are one commit.
- Never a commit that is only "wip", "fixes" or "more changes". Squash those before pushing.

### Message format

```
<type>: <imperative summary, 50 chars or fewer, no full stop>

<why this change exists, wrapped at 72 characters. What the reader
cannot get from the diff. The problem it solves, the decision you
made, the thing you deliberately did not do.>

<footers>
```

Rules:

- Imperative mood: "add model picker", never "added" or "adds".
- The subject says what. The body says why. If the why is obvious from the subject, no body is needed.
- Never put a model name, an assistant identifier or session chatter in a commit message.
- Reference issues in a footer, not in the subject line.

Good:

```
fix: rebuild the OpenAI client when the key changes

The client was constructed at module scope, so a key entered after the
first render was never used and every request failed with a 401. It is
now built inside the request path, keyed off session state.

Fixes #42
```

Bad: `update code`, `fixed bug`, `changes as discussed`.

## The pre-push gate

Run all of it. Every time. It takes under a minute and it is the difference between a clean PR and three follow-up commits.

```bash
git status                # nothing unexpected staged, nothing important unstaged
git diff --staged         # read every line you are about to publish
```

Then confirm each of these:

- [ ] The diff contains only files this task needed.
- [ ] No secrets, keys, tokens, `.env` files or personal data.
- [ ] No debug prints, stray `TODO`s, commented-out blocks or leftover instrumentation.
- [ ] Linter and formatter are clean.
- [ ] Tests run and pass, or the reply says exactly which did not and why.
- [ ] The commit message explains why, not just what.

If any line of the diff surprises you, stop and find out why before pushing.

## Push

```bash
git push -u origin <branch-name>
```

On a network failure, retry with backoff: 2s, 4s, 8s, 16s, then stop and report. Never force-push a branch anyone else may have checked out. On your own branch, prefer `--force-with-lease` over `--force`, and only when you know what you are overwriting.

## Pull requests

Open as a draft unless it is genuinely ready for a reviewer's time.

```markdown
## What

One or two sentences. The observable change, in the reader's terms.

## Why

The problem this solves. Link the issue if there is one.

## How

The approach, and any decision worth defending. Name what you
deliberately did not do.

## Verification

The commands you ran and what came back. Be specific.

- `ruff check .` clean
- 12 tests pass
- Ran the app, sent a message, response streamed correctly

## Risk

The one thing most likely to break, and how to spot it.
```

Check for a repository PR template first, at `.github/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE.md`. If one exists, use its headings instead of these.

## After opening

- Address every review comment: implement it, or reply explaining why not. Silence is not an answer.
- CI red is work now, not later. Reproduce the failure locally, fix the cause, push.
- Never skip, disable or quarantine a test to reach green.
- Never push an empty commit to re-trigger CI.

## Releases

- Tag only from a green, merged base.
- Semantic versioning: breaking is major, new behaviour is minor, fixes are patch.
- Release notes are written for the user, not the committer. Grouped as Added, Changed, Fixed, Removed.
- Know the rollback before you tag. If the answer is "we would have to hotfix", write down what the hotfix would be.

## Rollback

When something goes wrong in production, restore service first and understand second.

```bash
git revert <sha>      # safe: a new commit, history intact
```

Prefer `revert` over `reset` on anything already pushed. Once service is restored, take the incident to `ogenic-debug` and fix the root cause properly.
