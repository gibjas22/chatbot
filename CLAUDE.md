# Project memory

## Owner

Gibson Nyendwa. British English throughout. No em-dashes in any output: chat, code comments,
commit messages, documentation or pull request bodies.

## Installed skills

Two skills live in `.claude/skills/` and load automatically in this repository.

### Strix — security and safety guardian

`.claude/skills/strix/SKILL.md`

Runs on every task that touches code. Three gates:

1. **Reflex** on every file write: no hardcoded secrets, no secret in logs, untrusted input
   treated as data, no destructive command without looking first, least privilege by default.
2. **Pre-commit** before any commit, push or pull request:
   `bash .claude/skills/strix/scripts/scan.sh`
3. **Deep audit** on request or before a public release, using
   `.claude/skills/strix/references/audit-checklist.md`.

Strix never blocks ordinary work and never lectures. It fixes what it finds and says so in one line.

### Ogenic God Toolkit — code workflow

`.claude/skills/ogenic-god-toolkit/SKILL.md`

Seven phases for any non-trivial change: Orient, Plan, Guard, Build, Verify, Ship, Report.
No phase is skipped silently.

The rule that matters most is **evidence before assertion**. Never say fixed, working, passing
or complete without having run something that proves it. If tests fail, show the output. If a
check could not run here, say so and give Gibson the command.

Run every available quality gate in one pass:

```bash
bash .claude/skills/ogenic-god-toolkit/scripts/preflight.sh
```

## This project

A Streamlit chatbot calling a hosted LLM.

- Run: `streamlit run streamlit_app.py`
- Install: `pip install -r requirements.txt`
- No test suite yet. Adding logic worth testing means adding `pytest` and a `tests/` directory,
  not shipping untested behaviour.

Live risks for this stack, per Strix: API key exposure, prompt injection through chat input,
unbounded token cost, and XSS if model output is rendered as raw HTML. Detail in
`.claude/skills/strix/SKILL.md`.

## Git

Development happens on a feature branch, never directly on `main`. Push with
`git push -u origin <branch>` and open a draft pull request.
