# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

A Streamlit chatbot that talks to the OpenAI API, plus the **Ogenic God Mode
toolkit**: the Claude Code skills, slash commands and CI that govern how work
gets done here.

Two things live side by side, and they are not the same job:

| Path | Is |
|---|---|
| `streamlit_app.py`, `chat_errors.py` | The application |
| `.claude/`, `tools/ogenic/`, `docs/OGENIC_GOD_MODE.md` | The toolkit that governs how the application is changed |

## Commands

```bash
streamlit run streamlit_app.py                    # run the app
python -m unittest discover -s tests -t .         # run the tests
ruff check . && ruff format --check .             # lint and format
python3 tools/ogenic/validate_toolkit.py          # validate the skills
```

CI runs all four, plus a secret scan. Run them before pushing rather than
after, because a red build costs a cycle.

## Architecture

Small enough to hold in your head, so keep it that way.

- `streamlit_app.py` is the whole application: key input, chat history in
  `st.session_state`, one streaming call to the OpenAI API.
- `chat_errors.py` masks API keys out of error text. It exists as its own
  module so it can be tested, because printing a credential into the page is
  the expensive failure here.
- `tools/ogenic/` is standard library only, deliberately, so CI runs it with
  no install step.
- `tests/` uses `unittest`, not pytest, matching that same constraint.

## Conventions that matter

**Chat history is committed only on success.** The prompt is displayed
immediately but is not written to `st.session_state.messages` until the turn
completes. An earlier version appended first and rolled back on failure, which
left orphaned messages that were resent with every later turn. Do not
reintroduce that ordering.

**Never surface a raw OpenAI error.** Everything shown to a user goes through
`chat_errors.safe_error_text`, because OpenAI puts the offending key into the
message text of an authentication error.

**Dependencies are pinned to their major version.** `openai` has reached 3.x
while this code targets the 1.x interface. Moving majors is a deliberate,
tested migration, never a side effect.

**The format gate covers the whole repository.** New files must be
`ruff format` clean before they are committed.

**Test fixtures that contain key-shaped strings** must be excluded by name in
the CI secret scan, never by skipping `tests/` wholesale, so a credential
committed into a future test file is still caught.

## The workflow

This repository carries the Ogenic toolkit. Start with `/god-mode` to route a
task, or go straight to `/build`, `/secure` or `/ship`. The five stages are
Frame, Plan, Build, Verify, Ship, and each has a gate that produces an
artefact rather than an intention.

The account-level skills (`systematic-debugging`, `test-driven-development`,
`verification-before-completion`, `writing-plans`, `code-review`) own the
general engineering doctrine. The Ogenic skills carry only what is specific to
this repository and its house process. Where they disagree, the Ogenic skill
wins inside this repository.

## Things to know before changing something

- The app has no automated test covering the Streamlit flow itself, only the
  error redaction. Verify UI behaviour by running the app.
- `gpt-3.5-turbo` is still the model. Changing it is a cost and quality
  decision that belongs to Gibson, not a refactor.
- CI runs on pull requests and on pushes to `main` only. A branch with no open
  PR gets no CI.
