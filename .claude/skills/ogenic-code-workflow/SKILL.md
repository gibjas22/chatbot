---
name: ogenic-code-workflow
description: "The five-stage house workflow for this repository: Frame, Plan, Build, Verify, Ship. Use for any request to build, add, implement, change, extend, refactor or migrate code here, and whenever Gibson asks for the code workflow or how to approach a change. Covers the stage gates, the verification ladder and the definition of done, and delegates the general doctrine to the account-level skills that own it."
---

# Ogenic Code Workflow

Five stages. Each has a gate. You do not pass a gate by intending to, you pass it
by producing its artefact.

```
Frame ──▶ Plan ──▶ Build ──▶ Verify ──▶ Ship
  │         │         │         │         │
 goal +   ordered   working   evidence   commit +
 scope    steps      code     of green     PR
```

Small changes compress the stages, they never skip them. A one-line fix still
needs a framed goal and a verification step. It takes ninety seconds rather than
an hour.

## What this skill owns, and what it does not

This skill owns the **stages, the gates and the definition of done**. The craft
inside each stage belongs to skills that already do it better:

| Stage | Load this for the how |
|---|---|
| Plan | `writing-plans`, and `executing-plans` when handing off |
| Build | `test-driven-development` |
| Verify | `verification-before-completion` |
| Build, when stuck | `systematic-debugging` |
| Verify, self-review | `code-review`, then `requesting-code-review` |
| Ship | `ogenic-ship`, and `finishing-a-development-branch` |

Do not restate those here, and do not paraphrase them in your reply. Load them.

## Stage 1: Frame

Before touching a file, answer four questions in writing.

1. **What changes for the user?** The observable difference, not the implementation.
2. **What is in scope, and what is explicitly out?** Name the out-of-scope items,
   because that is what stops creep.
3. **What already exists?** See below.
4. **How will I know it works?** Name the check now, before you are invested.

**Gate:** a four-line frame. If you cannot write question 4, you do not
understand the task yet.

### Finding the existing pattern

Spend the first minutes reading, not typing. This repository is small enough to
survey properly.

```bash
ls                                      # what shape is this?
grep -rl "<the thing nearest to yours>" --include="*.py" .
```

At minimum, read the file you are about to change in full, the nearest existing
example of the thing you are adding, and the test that exercises it.

Then match what you find. Naming, error handling, comment density and structure
should look like the surrounding code wrote it. Matching an imperfect existing
pattern beats introducing a second, better one: two patterns is worse than one
mediocre pattern, because every future contributor has to choose. If there is
genuinely no precedent you are setting it, so say so and keep it plain.

For a new module, the minimum viable structure is the module with one real
function, its test with one real case, and the wiring that makes it reachable.
No abstract base class for one implementation, no config option nothing sets, no
`utils.py`, no folder tree of empty files.

## Stage 2: Plan

Load `writing-plans`. The house additions:

- Three to seven steps. Fewer means you have not thought it through, more means
  split the task.
- Name real files. "Update the backend" is not a step.
- Order steps so the tree is runnable after each one where possible.
- A decision you cannot make belongs at the top of the plan, not buried in step 5.

**Gate:** a numbered plan naming real files and a real verification command.

## Stage 3: Build

Load `test-driven-development`. The house additions:

- **One concern per change.** Do not fix formatting, rename a variable and add a
  feature in one pass. Each is cheap alone and unreviewable together.
- **Delete rather than comment out.** Git remembers. Commented-out code is a lie
  about intent.
- **No speculative generality.** Build for the second case when it arrives.
- **Handle the failure path.** Every network call, file read, parse and user
  input has a failure mode. Decide what happens.
- **Comment the why, never the what.**

When the plan turns out wrong, that is information. Say in one line what the code
taught you, revise the plan, continue. Do not improvise through six steps that no
longer match the plan you wrote.

**Gate:** the plan is worked through, and the code runs.

## Stage 4: Verify

Load `verification-before-completion`. Climb this ladder as far as the change
warrants; every change reaches at least rung 2.

| Rung | Check | Applies to |
|---|---|---|
| 1 | It parses and imports (`python -m compileall`) | Everything |
| 2 | `ruff check .` and `ruff format --check .` are clean | Everything |
| 3 | `python -m unittest discover -s tests -t .` passes | Any change to logic |
| 4 | A new test covers the new behaviour | New behaviour, fixed bugs |
| 5 | You ran the actual app and used the actual feature | Anything a user touches |
| 6 | Failure paths behave: bad input, no network, empty state | Anything with I/O |

Also run `python3 tools/ogenic/validate_toolkit.py` after touching any skill.

**Gate:** a written line naming what you ran and what came back.

## Stage 5: Ship

Load `ogenic-ship` for the pre-push gate and commit format.

## Definition of done

Every box, or the reply says which is unticked and why.

- [ ] The observable change from the Frame actually happened.
- [ ] Nothing in the "out of scope" list got built anyway.
- [ ] Verification ladder climbed to the right rung, with evidence.
- [ ] No secrets, keys or personal data in the diff.
- [ ] No debug prints, stray `TODO`s or commented-out blocks.
- [ ] The diff reads like the rest of the repository.
- [ ] Docs updated if behaviour a user relies on changed.
- [ ] The reply states what was done, what was verified, and what was not.

## Compression guide

| Change size | Frame | Plan | Verify rung |
|---|---|---|---|
| Typo, copy edit | one line | skip | 1 and 2 |
| Single function | three lines | three steps | 2 and 3 |
| Feature | full | full | 4 to 6 |
| Migration across files | full, plus rollback note | full, ordered to keep the tree green | 3 to 6 |
