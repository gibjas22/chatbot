# The seven phases, expanded

## 1. Orient

Questions to answer before touching anything:

- Which files does this actually change? Find them, do not guess.
- Does this codebase already solve a similar problem? Copy that shape.
- What is the test command? What is the run command? What is the lint command?
- What conventions are in force: naming, error handling, module layout, formatting?
- Is there a `CLAUDE.md`, `CONTRIBUTING.md` or a project skill with rules that override defaults?

Fast orientation commands:

```bash
git log --oneline -15
ls -R --ignore=.git --ignore=node_modules --ignore=__pycache__ | head -60
grep -rn "def main\|if __name__\|export default" --include='*.py' --include='*.ts' . | head
cat CLAUDE.md CONTRIBUTING.md 2>/dev/null
```

## 2. Plan

A good plan names files and states the order. A bad plan restates the request.

Bad: "Add authentication to the app."

Good:
1. Add `auth.py` with a `verify_token` function using the existing `settings` object.
2. Wrap the three protected routes in `app.py` with the new dependency.
3. Add `tests/test_auth.py` covering valid, expired and missing token.
4. Update `.env.example` with `AUTH_SECRET`.
Risk: sessions currently stored in memory will drop on restart. Out of scope, flagged.

Write the plan to a file when the work spans more than roughly five files, or when it will run
long enough that context might be summarised.

## 3. Guard

Ask, for this specific change:

- Does it read or write a secret?
- Does it accept input from a user, a file, a network response or a model?
- Does it delete, overwrite or migrate anything?
- Does it add a dependency?
- Does it change who can access what?

Any yes routes through the Strix reflex checks before the first line is written.

## 4. Build

Working order that avoids rework:

1. Types and data structures first. They constrain everything after.
2. The happy path.
3. The error path.
4. The tests.
5. The wiring into the rest of the app.

Stop and re-plan if you find yourself changing files that were not in the plan. Either the plan
was wrong, which is fine, or the scope is creeping, which is not.

## 5. Verify

Verification is a set of commands with visible output, not a feeling.

Minimum for any change:

```bash
# whatever the project uses
pytest -q            # or: npm test, go test ./..., cargo test
ruff check .         # or: eslint ., golangci-lint run
```

Then exercise the change directly. For a web app, start it and hit the path. For a library, call
the function with a real value. For a CLI, run it.

If nothing can be run here, write the exact commands Gibson should run and say clearly that they
have not been run.

## 6. Ship

```bash
git add -A
git commit -m "<type>: <what changed and why>"
bash .claude/skills/strix/scripts/scan.sh --range origin/main..HEAD
git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
```

On a network failure, retry up to four times with 2s, 4s, 8s, 16s backoff.

Open a draft pull request if the branch has none open.

## 7. Report

Structure:

**What changed.** Two or three sentences, no file listing unless the reader must go there.

**What was verified.** The commands run and their result. Failures included.

**What was not done.** Anything blocked, deferred or deliberately out of scope, with the reason.

**Next.** One step, or nothing. Never a menu of options.
