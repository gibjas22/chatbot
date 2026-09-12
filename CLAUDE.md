# Project memory

## Owner

Gibson Nyendwa. British English in all prose, code comments, commits and pull request bodies.
No em-dashes anywhere.

## Installed toolkit

Eight skills live in `.claude/skills/`, with slash commands in `.claude/commands/`. They load
automatically in this repository. Full documentation: `docs/OGENIC_GOD_MODE.md`.

### Ogenic God Mode

`ogenic-god-mode` is the router. It sets the posture and picks the right skill, then hands off to
one of: `ogenic-code-workflow` for building, `ogenic-scaffold` for new code, `ogenic-debug` for
failures, `ogenic-review` for judging existing code, `ogenic-secure` for security discipline, and
`ogenic-ship` for commits, pushes and releases.

Start any engineering task there rather than loading every skill.

### Strix

`strix` is the exception to the router. It is not something you choose, it runs on every task.

- **Reflex checks** on every file write: no secret in a tracked file, no secret in a log, untrusted
  input treated as data, no destructive command without reading the target, least privilege by
  default.
- **A scanner** before every commit or push: `bash .claude/skills/strix/scripts/scan.sh`
- **A deep audit** on request or before a public release.

`ogenic-secure` is the standing discipline, Strix is the watch that enforces it. Read the first
for the rules and the second for when they fire.

## The rule that matters most

Evidence before assertion. Never report something as fixed, working, passing or complete without
having run a command that proves it. If a check failed, show the output. If it could not run here,
say so plainly and give Gibson the command.

## This project

A Streamlit chatbot calling a hosted LLM.

- Run: `streamlit run streamlit_app.py`
- Install: `pip install -r requirements.txt`
- Validate the toolkit: `python tools/ogenic/validate_toolkit.py`
- Tests: `pip install -r requirements-dev.txt` then `python -m pytest tests/ -q`
- The safety and cost rules live in `chat_core.py`, deliberately free of Streamlit and OpenAI
  imports so they can be tested without a UI, a network call or a paid key. New logic worth
  testing belongs there rather than inline in the app.
- Ruff is pinned. Verify with the pinned version, not whichever binary is first on PATH, because
  a newer ruff enables new rules by default and will disagree with CI.

CI runs four jobs on every push: toolkit validation, lint and compile, tests, and a secret scan. See
`.github/workflows/ogenic-code-workflow.yml`.

The application risks Strix recorded were addressed in pull request #6: conversation cost and
request usage are bounded, provider errors are redacted rather than shown as tracebacks, and both
render paths sanitise model output. Two of the four were overstated in the original record and the
correction is kept in `.claude/skills/strix/SKILL.md`, because overstating a risk spends the same
credibility as missing one.

One limitation stands. Strix runs locally before a push but is not enforced in CI, which runs its
own simpler credential grep.

## Git

Work on a feature branch, never directly on `main`. Push with `git push -u origin <branch>` and
open a draft pull request.
