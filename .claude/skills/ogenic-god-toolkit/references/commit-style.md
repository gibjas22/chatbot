# Commit and pull request conventions

## Commit messages

Format:

```
<type>: <imperative summary under 72 characters>

<why this change exists, and anything a reviewer would otherwise have to ask>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `security`.

Good:

```
fix: stop chat history growing without bound

Session state kept every turn, so token cost rose linearly across a long
conversation and eventually exceeded the model context limit. Trims to the
last 20 turns before each request.
```

Bad:

```
Update streamlit_app.py
```

Rules:

- One concern per commit. A fix and a refactor are two commits.
- Write why, not what. The diff already says what.
- No em-dashes.
- No model name or version in the message.
- Attribution lines go at the end when the session requires them.

## Pull requests

Check for a template first: `.github/pull_request_template.md`,
`.github/PULL_REQUEST_TEMPLATE.md`, root `PULL_REQUEST_TEMPLATE.md`, `docs/PULL_REQUEST_TEMPLATE.md`.
If one exists, mirror its headings and fill them from the diff.

Without a template, use:

```markdown
## What

One paragraph on what this changes and why it was needed.

## How

The approach, and any decision a reviewer would question.

## Verification

The commands run and their output. Say plainly if something was not run.

## Notes

Anything out of scope, deferred, or worth a second opinion.
```

Open as a draft. Never describe an unrun check as passing.

## Branching

Work on the designated branch. Never push to `main` without explicit permission. If the branch's
pull request is already merged, restart the branch from the latest default branch rather than
stacking new commits on merged history.
