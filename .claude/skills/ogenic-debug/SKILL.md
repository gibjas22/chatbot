---
name: ogenic-debug
description: "Systematic debugging for the Ogenic toolkit: reproduce, isolate, hypothesise, fix the root cause, prove it. Use whenever something is broken, failing, erroring, crashing, hanging, flaky or behaving unexpectedly, and whenever Gibson asks why something is not working. Replaces guess-and-patch with a bisecting loop that terminates."
---

# Ogenic Debug

Guessing feels faster and is not. The loop below terminates. Guessing does not.

```
Reproduce ──▶ Isolate ──▶ Hypothesise ──▶ Test ──▶ Fix root cause ──▶ Prove
     ▲                                      │
     └──────────── hypothesis wrong ────────┘
```

## Step 1: Reproduce

You cannot fix what you cannot trigger. Before any theory, get a command or a sequence of clicks that fails every time.

- Write down the exact reproduction: input, environment, command, and the precise failure text.
- Copy the real error, all of it, including the stack trace. Not your summary of it.
- If it is intermittent, run it in a loop and record the failure rate. "Sometimes" is not a specification, "roughly one run in five" is.
- If you genuinely cannot reproduce it, say so and gather evidence instead: logs, the user's exact steps, version differences. Do not fix a bug you have never seen.

**Never skip this to save time.** A fix for a bug you never reproduced cannot be verified, so you will not know whether you fixed it.

## Step 2: Isolate

Halve the search space until the fault has nowhere to hide.

- **Read the stack trace properly.** The top frame is where it surfaced, which is often not where it started. Walk down to the first frame in your own code.
- **Bisect the input.** Half the data, half the config, half the request. Which half still fails?
- **Bisect the code path.** Comment out or short-circuit a branch. Does the failure survive?
- **Bisect history.** If it used to work, `git log` the touched files and `git bisect` if the range is wide.
- **Remove variables.** Does it fail with the network stubbed? With a fresh cache? On a clean checkout? Outside the container?

Stop when you can point at a single function, one dependency version, or one line of configuration.

## Step 3: Hypothesise

State the theory in one falsifiable sentence, with a mechanism.

- Good: "The API key is read once at import, so a key entered after the first render is never used by the client."
- Bad: "Something is wrong with the state handling."

A theory without a mechanism is a guess. If you cannot describe the causal chain from cause to symptom, you are not ready to change code.

Rank candidates by prior probability, and start at the top:

1. Your own change, made in the last hour.
2. A wrong assumption about an API or library behaviour.
3. State that outlives what you expected: caches, session state, module-level globals, singletons.
4. An ordering or timing problem: initialisation order, race, async not awaited.
5. Environment drift: version, path, encoding, locale, timezone, permissions.
6. A genuine bug in a third-party library. Last, always, because it usually is not.

## Step 4: Test the hypothesis

Design the cheapest test that can prove you wrong, not one that confirms you.

- Add one targeted log or print at the boundary the theory names, and read the actual value.
- Assert the invariant you believe holds. If it holds, your theory is dead. Kill it and go back to step 3.
- Change one thing at a time. Two simultaneous changes tell you nothing about either.

Remove every instrument you added before you finish. Debug prints in a diff are a review failure.

## Step 5: Fix the root cause

The fix goes where the wrong behaviour originates, not where it became visible.

Symptom fixes to refuse:

- Wrapping in a broad `try/except` that swallows the error rather than handling it.
- Adding a sleep or retry to hide a race.
- Special-casing the one input that reproduced the failure.
- Widening a type or loosening validation so the bad value passes through quietly.

If a symptom fix is genuinely the right call, for instance a real upstream bug with no available patch, say so in a comment naming the upstream issue and the condition for removing the workaround.

Ask two questions of every fix:

1. **Where else does this pattern appear?** The same mistake is usually in three places.
2. **What made this possible?** If a missing check allowed it, add the check. That is what stops the next one.

## Step 6: Prove it

- The original reproduction now passes. Run it, do not assume it.
- Add a regression test that fails against the old code and passes against the new. If you cannot write one, say why in the reply.
- Run the surrounding tests. Root-cause fixes have wider effects than symptom patches, which is the point, and also the risk.
- Describe the fix by its mechanism: "the client was built once at import, so it now rebuilds when the key changes", not "fixed the key bug".

## Time boxes

| Elapsed | Do this |
|---|---|
| 20 minutes, no reproduction | Stop theorising. Go and gather evidence: logs, versions, exact user steps |
| 3 failed hypotheses | Your model of the system is wrong. Go back and read the code you assumed you understood |
| 45 minutes, no progress | Write down what you have ruled out, then say so in the reply. A well-documented dead end is worth more than another hour of the same loop |

## Flaky failures

Treat flakiness as a real bug with a probability attached, never as noise to re-run away.

- Run it 20 times, record the rate. That number is your before-and-after measure.
- The usual causes: shared state between tests, real clocks, real network, ordering dependence, unawaited async work, a fixed port or temp path.
- A test that is skipped or quarantined is not fixed. Never disable a test to get to green.
