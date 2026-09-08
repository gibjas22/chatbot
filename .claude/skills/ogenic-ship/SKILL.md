---
name: ogenic-ship
description: "The pre-push gate, commit message format and pull request conventions for this repository. Use when Gibson asks to commit, push, open a PR, merge, tag or release, and as the final stage of ogenic-code-workflow. Load finishing-a-development-branch alongside it for the decision about how to integrate completed work."
---

# Ogenic Ship

Shipping is a discipline, not a keystroke. The gate below runs before every push.

For the decision about **how to integrate** finished work, load
`finishing-a-development-branch`. This skill covers the mechanics of getting a
sound commit onto a branch and into a PR.

## Branches

- Never commit directly to `main`. Branch first.
- One branch, one purpose. If the name needs "and", it is two branches.
- `<type>/<short-kebab-summary>`, where type is `feat`, `fix`, `chore`, `docs`,
  `refactor`, `style`, `test` or `ci`.
- Branch from an up-to-date base.

## Commits

One commit, one logical change. A reviewer should be able to read a commit,
understand it, and accept or reject it on its own.

- Split formatting from behaviour. A rename mixed into a logic change hides the
  logic change.
- A commit should leave the tree working.
- Never "wip", "fixes" or "more changes". Squash those before pushing.

```
<type>: <imperative summary, 50 chars or fewer, no full stop>

<why this change exists, wrapped at 72 characters. What the reader cannot
get from the diff: the problem it solves, the decision you made, the thing
you deliberately did not do.>

<footers>
```

Imperative mood: "add model picker", never "added". The subject says what, the
body says why. **Never put a model name, an assistant identifier or session
chatter in a commit message.**

## The pre-push gate

Run all of it, every time. Under a minute, and it is the difference between a
clean PR and three follow-up commits.

```bash
git status
git diff --staged                                  # read every line
ruff check . && ruff format --check .
python -m unittest discover -s tests -t .
python3 tools/ogenic/validate_toolkit.py
```

Then confirm:

- [ ] The diff contains only files this task needed.
- [ ] No secrets, keys, `.env` files or personal data.
- [ ] No debug prints, stray `TODO`s or commented-out blocks.
- [ ] The commit message explains why, not just what.

Then read your own diff adversarially: **what would make CI reject this?** That
question has caught a secret-scan collision and a format failure in this
repository already. Fix what you find before pushing, not after.

If any line of the diff surprises you, find out why before pushing.

## Push

```bash
git push -u origin <branch-name>
```

On network failure, retry with backoff (2s, 4s, 8s, 16s), then report. Never
force-push a branch someone else may have checked out. On your own branch prefer
`--force-with-lease`, and only when you know what you are overwriting.

## Pull requests

Open as a draft unless it is genuinely ready for a reviewer's time.

```markdown
## What      One or two sentences, the observable change.
## Why       The problem this solves.
## How       The approach, and what you deliberately did not do.
## Verification   The commands you ran and what came back, specifically.
## Risk      The one thing most likely to break, and how to spot it.
```

Check for a repository PR template first and use its headings if one exists.

### After opening

- Address every review comment: implement it, or reply explaining why not.
- CI red is work now. Reproduce locally, fix the cause, push.
- Never skip, disable or quarantine a test to reach green.
- Never push an empty commit to re-trigger CI.

## Rollback

Restore service first, understand second.

```bash
git revert <sha>      # safe: a new commit, history intact
```

Prefer `revert` over `reset` on anything already pushed. Once service is
restored, take it to `systematic-debugging` and fix the root cause properly.
