---
name: ogenic-code-workflow
description: "The five-stage Ogenic code workflow: Frame, Plan, Build, Verify, Ship. Use for any request to build, add, implement, change, extend, refactor or migrate code, and whenever Gibson asks for the code workflow, the build process, or how to approach a change. Covers stage gates, plan format, build discipline, the verification ladder and the definition of done."
---

# Ogenic Code Workflow

Five stages. Each has a gate. You do not pass a gate by intending to, you pass it by producing its artefact.

```
Frame ──▶ Plan ──▶ Build ──▶ Verify ──▶ Ship
  │         │         │         │         │
 goal +   ordered   working   evidence   commit +
 scope    steps      code     of green     PR
```

Small changes compress the stages, they never skip them. A one-line fix still needs a framed goal and a verification step. It simply takes ninety seconds rather than an hour.

## Stage 1: Frame

Before touching a file, answer four questions in writing.

1. **What changes for the user?** Describe the observable difference, not the implementation.
2. **What is in scope, and what is explicitly out?** Name the out-of-scope items, because that is what stops creep.
3. **What already exists?** Read the neighbouring code first. Most tasks are extensions of a pattern already in the repository.
4. **How will I know it works?** Name the check now, before you are invested in the code.

**Gate:** a four-line frame. If you cannot write question 4, you do not understand the task yet.

### Reading before writing

Spend the first minutes reading, not typing. At minimum:

- The file you are about to change, in full, not just the function.
- The nearest existing example of the thing you are adding.
- The test or entry point that exercises it.

Match what you find. Naming, error handling, comment density and structure should look like the surrounding code wrote it. Consistency beats your personal preference every time.

## Stage 2: Plan

Write the steps before the code. The plan is for you, so keep it terse, but keep it real.

```markdown
## Plan: <short title>

1. <file>: <what changes, in one clause>
2. <file>: <what changes>
3. Verify: <exact command or manual check>

Risk:  <the one thing most likely to break>
Out:   <what this deliberately does not do>
```

Rules for a good plan:

- Order steps so the tree is runnable after each one where possible.
- Three to seven steps. Fewer means you have not thought it through, more means split the task.
- Name real files. "Update the backend" is not a step.
- If a step needs a decision you cannot make, that is the escalation point, and it belongs at the top of the plan, not buried in step 5.

**Gate:** a numbered plan naming real files and a real verification command.

## Stage 3: Build

Work the plan in order, one step at a time.

### Build discipline

- **One concern per change.** Do not fix formatting, rename a variable and add a feature in the same pass. Each is cheap alone and unreviewable together.
- **Make it work, then make it clean.** But do not stop after "work". The clean pass is part of the step, not a future task.
- **Delete rather than comment out.** Git remembers. Commented-out code is a lie about intent.
- **No speculative generality.** No configuration option, abstraction layer or plugin hook that nothing currently uses. Build for the second case when the second case arrives.
- **Handle the failure path.** Every network call, file read, parse and user input has a failure mode. Decide what happens, do not leave it to chance.
- **Comment the why, never the what.** The code says what. A comment earns its place by explaining a decision that is not obvious from reading.

### When the plan turns out wrong

It will, sometimes. That is information, not failure. Stop, say in one line what the code taught you, revise the plan, then continue. Do not quietly improvise your way through six steps that no longer match the plan you wrote.

**Gate:** the plan is worked through, and the code runs.

## Stage 4: Verify

Climb the ladder as far as the change warrants. Every change reaches at least rung 2.

| Rung | Check | Applies to |
|---|---|---|
| 1 | It parses and imports. `python -m compileall`, a build, a typecheck | Everything |
| 2 | The linter and formatter are clean | Everything |
| 3 | Existing tests still pass | Any change to logic |
| 4 | A new test covers the new behaviour | New behaviour, fixed bugs |
| 5 | You ran the actual application and used the actual feature | Anything a user touches |
| 6 | The failure paths behave: bad input, no network, empty state | Anything with I/O or user input |

### The evidence rule

State outcomes as what you observed.

- Good: "ruff clean, 12 tests pass, ran the app and sent a message, response streamed correctly."
- Good: "Could not run the Streamlit app in this environment, so I verified by import and by reading the diff. Untested at runtime."
- Not acceptable: "Everything should work now."

If a check fails, that is the result. Report it with the output and fix it. Never report green for a check you skipped.

**Gate:** a written line naming what you ran and what came back.

## Stage 5: Ship

Hand over to `ogenic-ship` for commits, branch and PR discipline. Before you do, run the definition of done.

## Definition of done

Every box, or the reply says which one is unticked and why.

- [ ] The observable change from the Frame actually happened.
- [ ] Nothing in the "out of scope" list got built anyway.
- [ ] Verification ladder climbed to the right rung, with evidence.
- [ ] No secrets, keys or personal data in the diff.
- [ ] No debug prints, stray `TODO`s or commented-out blocks left behind.
- [ ] The diff reads like the rest of the repository.
- [ ] Docs or README updated if behaviour a user relies on changed.
- [ ] The reply states plainly what was done, what was verified, and what was not.

## Worked example

> "Add a model picker to the chatbot."

```
Frame
  Change:  the user picks a model in the sidebar instead of gpt-3.5 being hardcoded
  In:      sidebar control, pass selection to the API call, keep the default working
  Out:     per-model pricing display, model-specific parameter tuning
  Exists:  streamlit_app.py holds the whole app, key handled by st.text_input
  Check:   run the app, switch model, confirm the reply still streams

Plan
  1. streamlit_app.py: add MODELS constant with the supported ids
  2. streamlit_app.py: st.sidebar.selectbox bound to session state, default first entry
  3. streamlit_app.py: pass the selection into client.chat.completions.create
  4. README.md: note the picker in the feature list
  5. Verify: ruff, run the app, switch model mid-conversation
  Risk: switching mid-conversation sends prior messages to a model that may reject them
  Out:  no cost estimation

Build   → four small edits, one concern each
Verify  → rung 5: ruff clean, app run, switched model, reply streamed
Ship    → ogenic-ship
```

## Compression guide

| Change size | Frame | Plan | Verify rung |
|---|---|---|---|
| Typo, copy edit | one line | skip | 1 and 2 |
| Single function | three lines | three steps | 2 and 3 |
| Feature | full | full | 4 to 6 |
| Migration, refactor across files | full, plus a rollback note | full, plus step ordering that keeps the tree green | 3 to 6 |
