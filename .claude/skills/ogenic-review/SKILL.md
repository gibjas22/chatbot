---
name: ogenic-review
description: "Review code against the Ogenic bar: correctness, failure paths, security, clarity and fit. Use when Gibson asks for a review, an audit, a second opinion, whether code is good, or before opening a pull request. Also the self-review pass at the end of ogenic-code-workflow. Produces ranked findings with file, line, cause and fix."
---

# Ogenic Review

Review in one direction: what would hurt in production, worst first. Style opinions come last or not at all.

## Order of passes

Do them in this order. Do not drift between them, because mixing passes is how a correctness bug gets missed while you are renaming a variable.

1. **Correctness.** Does it do what it claims, including at the edges?
2. **Failure paths.** What happens when the thing it depends on fails?
3. **Security and data.** Secrets, injection, exposure, permissions.
4. **Fit.** Does it match the repository it now lives in?
5. **Clarity.** Could a new starter change this safely in six months?
6. **Efficiency.** Only where it is measurably a problem.

## Pass 1: Correctness

- Off-by-one, inclusive versus exclusive bounds, and the empty case.
- `None`, empty string, empty list, zero, and the "not set yet" state. Zero and absent are different things, and code that conflates them is a bug waiting for the right input.
- Conditions that should be `and` but are `or`, and negations that read backwards.
- Loops that mutate what they iterate.
- State that persists between runs, requests or reruns when it should not, and state that resets when it should not.
- Copy versus reference. Mutating a caller's object is rarely intended.
- Every early return. Does each leave the system in a valid state?

## Pass 2: Failure paths

For every external call, ask: what if it is slow, what if it errors, what if it returns something unexpected?

- Unhandled exceptions on network, file and parse operations.
- Broad `except:` or `except Exception:` that swallows and continues.
- No timeout on a network call. A hang is worse than an error, because nothing alerts.
- Retries without a bound or a backoff.
- Partial failure: half the work committed and then a crash. Is that recoverable?
- Error messages that tell the user nothing they can act on, or that leak internals into the interface.

## Pass 3: Security and data

Hand off to `ogenic-secure` for the full checklist. At review time, always check:

- Credentials in code, config, tests, fixtures, logs or commit messages.
- User input reaching a shell, a query, a file path, an eval or an HTML render without escaping.
- Personal data written to logs.
- A dependency added without a reason, or pinned to nothing.
- Secrets echoed back into the interface, including in error text.

## Pass 4: Fit

- Does it use the helper that already exists, or has it reinvented one?
- Does it match local naming, error handling and structure?
- Is a new dependency justified when twenty lines of the standard library would do?
- Is it in the right file? A new concern in an already-crowded module is a smell.

## Pass 5: Clarity

- Names that describe intent rather than type or mechanism.
- Functions doing one thing. If the docstring needs "and", split it.
- Nesting beyond three levels. Guard clauses usually flatten it.
- Magic numbers and strings that deserve a name.
- Comments explaining why, not what. Delete any comment that restates the line beneath it.
- Dead code, unused imports, commented-out blocks.

## Pass 6: Efficiency

Only raise it where it bites in practice:

- A query or an API call inside a loop.
- Work repeated per iteration that could be hoisted.
- Loading a whole file or result set to use one field.
- A cache that is never invalidated.

Do not raise micro-optimisation on code that runs once.

## Finding format

Rank by severity, most severe first. Every finding needs a concrete failure, not a feeling.

```markdown
### [Critical|High|Medium|Low] <one-line claim>
`path/to/file.py:42`

**Fails when:** <specific input or state> produces <specific wrong outcome>.
**Cause:** <the mechanism, in one sentence>
**Fix:** <the concrete change>
```

Severity:

| Level | Means |
|---|---|
| Critical | Data loss, security exposure, or it does not work at all |
| High | Breaks on realistic input, or fails silently |
| Medium | Correct today, fragile under a likely change |
| Low | Clarity or consistency, no behavioural risk |

## Verify before you report

Every finding gets challenged before it goes in the list. Ask: is there a guard earlier in the call path that makes this impossible? Is the caller already validating this? Have I actually read the function I claim is wrong, or only its name?

A confident, wrong finding costs more trust than a missed one. Drop anything you cannot defend with a specific failing input.

## Closing the review

End with the state, plainly:

- Nothing found: "Reviewed <n> files across <the passes>. No findings. <what you checked most carefully>."
- Findings: the ranked list, then one line on the single thing to fix first.

Do not pad a clean review with invented nits.
