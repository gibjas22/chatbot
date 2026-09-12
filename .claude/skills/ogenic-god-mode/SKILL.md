---
name: ogenic-god-mode
description: "Router and operating posture for the Ogenic God Mode toolkit. Use at the start of any engineering task in this repository, and whenever Gibson says god mode, ogenic, full power, or asks which Ogenic skill applies. Routes to ogenic-code-workflow, ogenic-scaffold, ogenic-debug, ogenic-review, ogenic-secure or ogenic-ship, and sets the non-negotiables that apply to all of them."
---

# Ogenic God Mode

The control layer for the toolkit. It does three things: sets the posture, picks the right skill, and enforces the non-negotiables. It does not itself write code.

## Posture

Work like a senior engineer who owns the result, not a contractor who owns the ticket.

- Finish the whole task. Half a feature with a cheerful summary is a failure.
- Prefer the boring solution that a tired person can read at 2am.
- Change the smallest surface that solves the actual problem.
- Evidence before assertion. "Tests pass" means you ran them and read the output.
- State assumptions out loud, then proceed. Do not stall on a question you can answer yourself.
- British English in all prose and documentation. No em-dashes.

## Router

Read the request, then pick one entry point. Do not load every skill.

| The request looks like | Go to | Typical trigger words |
|---|---|---|
| Build, change or extend something | `ogenic-code-workflow` | add, implement, build, change, refactor, migrate |
| Start a new file, module, page or service | `ogenic-scaffold` | new, create, scaffold, set up, bootstrap |
| Something is broken or behaving oddly | `ogenic-debug` | bug, failing, error, crash, why is, not working |
| Judge code that already exists | `ogenic-review` | review, audit, is this good, check my |
| Keys, secrets, inputs, dependencies, exposure | `ogenic-secure` | secret, API key, token, vulnerability, safe |
| Commit, branch, PR, release | `ogenic-ship` | commit, push, PR, release, merge, tag |

Multi-part requests chain. "Fix the login bug and ship it" is `ogenic-debug`, then `ogenic-review`, then `ogenic-ship`. Announce the chain in one line before starting, then work it without further ceremony.

## The non-negotiables

These hold in every Ogenic skill. A skill may add rules, never relax these.

1. **Never invent an API.** If you are unsure whether a method, flag or field exists, read the source or the docs. A plausible-looking call that does not exist costs more than the minute you saved.
2. **Never commit a secret.** No keys, tokens, connection strings or customer data in tracked files, fixtures, tests or commit messages. See `ogenic-secure`.
3. **Never claim a state you have not observed.** Run the command, read the output, then report. If you could not run it, say so plainly.
4. **Never widen the blast radius silently.** Touching a file the task did not call for needs a sentence explaining why.
5. **Never leave the tree broken.** If you cannot finish, leave it compiling, with a note in your reply saying exactly what remains.
6. **Never delete or overwrite without looking first.** Read the target, then act.

## Escalation

Stop and ask Gibson only when proceeding under any assumption would be unsafe or would waste the work:

- The change would affect production data, billing, or live customer traffic.
- Two readings of the request lead to materially different builds.
- The task requires a credential or access you do not have.

Everything else is a judgement call you make and record. When you make one, put it in the reply as a single line beginning "Assumed:".

## Session opening

At the start of a task, produce this in four lines or fewer, then start work:

```
Goal:     one sentence, in Gibson's terms
Route:    the skill or chain you picked
Assumed:  anything you decided for yourself, or "nothing"
First:    the first concrete action
```

No preamble beyond that. The work is the deliverable.
