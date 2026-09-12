---
name: ogenic-god-toolkit
description: God mode code workflow for Gibson Nyendwa. Use this skill for any non-trivial coding work - building a feature, fixing a bug, refactoring, adding tests, wiring an integration, reviewing a diff, planning an implementation, debugging a failure, or shipping a change to a branch or pull request. Trigger it when Gibson says god mode, GOD MODE, ogenic, toolkit, build this, ship this, fix this properly, do it end to end, or asks for a full implementation rather than a snippet. Do not use it for a one-line answer, a syntax question, or a pure explanation.
---

# Ogenic God Toolkit

God mode is not permission to move fast and break things. It is a standing commitment to finish
the whole job: understand, plan, build, verify, ship, and report honestly. Gibson gets a working
result, not a plausible-looking draft.

## The seven phases

Every non-trivial task runs through these. Small tasks compress phases into a sentence each.
Large tasks give each phase real work. No phase is ever skipped silently.

### 1. Orient

Read before writing. Find the files that matter, the existing conventions, the test command, and
the way this codebase already solves the problem. Never invent a pattern the project already has.

Deliverable: a one-line statement of what the change actually touches.

### 2. Plan

State the approach in three to eight steps before the first edit. Name the files. Name the risk.
If two approaches are viable, pick one, say why in a sentence, and move.

Deliverable: a numbered plan. For anything above roughly five files or two hours of work, write
it to a file so it survives a context reset.

### 3. Guard

Run Strix Gate 1 over the plan. Anything touching secrets, user input, auth, deletion, network
calls or dependencies gets the reflex checks before code is written, not after.

Deliverable: named risks, or the word none.

### 4. Build

Write the code. Standing rules:

- Match the codebase. Its naming, its structure, its error style, its formatting.
- Smallest change that fully solves it. No speculative abstraction, no unrequested refactor
  riding along in the same diff.
- Handle the error path. Every call that can fail gets a decision about what happens when it does.
- No placeholder, no `TODO`, no stubbed function presented as finished. If something genuinely
  cannot be completed, it is called out explicitly, not buried.
- Comments explain why, never what.

### 5. Verify

This is the phase that separates god mode from guessing. A claim of "done" without evidence is
not permitted.

- Run the tests. Paste the real result, pass or fail.
- Run the linter and type checker if the project has them.
- Exercise the actual change: run the app, hit the endpoint, call the function.
- Re-read your own diff adversarially. What breaks this? Fix it before showing it.

If verification cannot run in this environment, say exactly that and say what Gibson needs to run.
Never describe an unrun test as passing.

### 6. Ship

- Commit on the designated branch with a message that says what changed and why.
- Run the Strix pre-commit scan before pushing.
- Push with `git push -u origin <branch>`, retrying on network failure with backoff.
- Open a draft pull request if none is open for the branch.

### 7. Report

Close with a recap that stands alone for someone who did not watch the work:

- What was built, in plain words.
- What was verified, with the evidence.
- What was not done, and why.
- The one next step, if there is one.

## Standing rules

**Finish the whole ask.** If part of the scope is blocked, complete everything else in full and
say plainly what was left and why. Scaling the work down is Gibson's call, not yours.

**Evidence before assertion.** Never say fixed, working, passing or complete without having run
something that proves it.

**Report failure faithfully.** If tests fail, show the output. A hedged claim is worse than a
clear no.

**One concern per commit.** A bug fix and a refactor do not share a diff.

**Do not ask permission to do the work.** Make the routine judgement calls. Stop only for a
destructive action or a genuine scope change.

**No em-dashes in anything written for Gibson**, in chat, in commits, in code comments, in
documentation. British spelling throughout.

## Debugging protocol

When something fails, do not pattern match to a fix. Work the loop:

1. **Reproduce.** Get the failure to happen on demand. If you cannot reproduce it, you cannot
   claim to have fixed it.
2. **Read the actual error.** The whole trace, not the last line.
3. **Form one hypothesis.** State it out loud.
4. **Test the hypothesis cheaply.** A print, a log line, a single assertion.
5. **Fix the cause, not the symptom.** A swallowed exception or a broadened try block is not a fix.
6. **Prove it.** Re-run the reproduction. Show it passing.

If three hypotheses fail in a row, stop and question the assumption underneath all three.

## Review protocol

When reviewing a diff, look for these in order:

1. Correctness. Does it do what it claims, including at the edges: empty, null, zero, huge,
   concurrent, and the second call.
2. Security. Run Strix Gate 2 thinking over the diff.
3. Failure handling. What happens when the network, the disk or the dependency is down.
4. Reuse. Does the codebase already have this.
5. Simplicity. What can be deleted without losing behaviour.

Report each finding with the file, the line, the concrete failure scenario and the fix. A finding
without a failure scenario is an opinion, and belongs in a short notes section.

## Quality bar

A change is finished when all of these hold:

- [ ] It does the whole thing that was asked.
- [ ] Tests pass, and the output was actually seen.
- [ ] Linter and type checker are clean, if the project has them.
- [ ] No secret, no debug leftover, no commented out code in the diff.
- [ ] The error path is handled.
- [ ] It reads like the rest of the codebase wrote it.
- [ ] Strix pre-commit scan is clean or every finding is a reviewed false positive.
- [ ] The recap tells the truth about what was verified.

## Reference files

- `references/workflow.md` — the phases expanded, with prompts to ask at each one.
- `references/quality-gates.md` — language specific commands for verification.
- `references/commit-style.md` — commit and pull request conventions.
- `scripts/preflight.sh` — runs the available checks for this project in one pass.
