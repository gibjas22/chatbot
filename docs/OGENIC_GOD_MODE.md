# Ogenic God Mode toolkit

A set of Claude Code skills, slash commands and CI checks that turn an ad-hoc
coding session into a repeatable engineering workflow: frame the task, plan it,
build it, verify it with evidence, then ship it properly.

Everything here is plain Markdown and two small scripts. There is no runtime
dependency, nothing to compile, and nothing that phones home.

## What is installed

### Skills, in `.claude/skills/`

| Skill | Does |
|---|---|
| `ogenic-god-mode` | The router. Picks the right skill for the request and sets the non-negotiables that apply to all of them |
| `ogenic-code-workflow` | The five-stage workflow: Frame, Plan, Build, Verify, Ship. Stage gates, plan format, verification ladder, definition of done |
| `ogenic-scaffold` | Starting new code well: finding the existing pattern, minimum viable structure, the anti-patterns that age badly |
| `ogenic-debug` | Reproduce, isolate, hypothesise, fix the root cause, prove it. With time boxes so the loop terminates |
| `ogenic-review` | Six ordered review passes, ranked findings, and a rule against reporting anything you cannot defend |
| `ogenic-secure` | Secrets, input handling, dependencies and data exposure. Including what to do when a key has already been committed |
| `ogenic-ship` | Commit granularity, message format, the pre-push gate, PR bodies, releases and rollback |
| `strix` | The always-on safety watch. Three gates, a working pre-commit scanner, and the deep audit checklist |

Skills load on demand. Claude reads the description in each file's frontmatter
and pulls in the body only when the task matches, so having seven installed
costs nothing until one is needed.

### Slash commands, in `.claude/commands/`

| Command | Runs |
|---|---|
| `/god-mode <task>` | Route the task and set the posture |
| `/build <change>` | The full five-stage code workflow |
| `/debug <symptom>` | The debugging loop |
| `/review <target>` | The review passes, ranked findings |
| `/secure <target>` | The security pass |
| `/ship` | Pre-push gate, commit, push, draft PR |
| `/strix [target]` | Run the Strix scan and report findings |

### Tooling, in `tools/ogenic/`

- `validate_toolkit.py` checks every skill and command: frontmatter present and
  well formed, name matching its directory, a description long enough and
  specific enough to trigger, a non-empty body, and no credentials sitting in
  any of it. Standard library only, so it runs anywhere Python 3 runs.
- `install.sh` copies the toolkit into another project or into your user
  configuration, with `--dry-run`, `--force` and `--uninstall`.

### CI, in `.github/workflows/ogenic-code-workflow.yml`

Three jobs, matching the verification ladder:

- **toolkit** validates the skills and commands, and proves a dry-run install
  writes nothing.
- **verify** compiles all Python, runs `ruff check` across the repository and
  `ruff format --check` across `tools/`.
- **secrets** scans every tracked file for credential patterns and fails the
  build on a hit.

## Using it

In a Claude Code session in this repository, the skills are picked up
automatically. Start with the router:

```
/god-mode add a model picker to the sidebar
```

Or go straight to a stage:

```
/build add streaming error handling to the chat loop
/debug the app 401s after I paste a valid key
/review staged
/secure staged
/ship
```

You do not have to use the commands. Asking in plain language works too, because
each skill's description tells Claude when to reach for it. The commands simply
remove the ambiguity when you want a specific process.

## Installing it elsewhere

Into another project:

```bash
./tools/ogenic/install.sh --target ../my-other-project
```

Into your user configuration, so it is available in every project on the
machine:

```bash
./tools/ogenic/install.sh --user
```

See what would happen without writing anything:

```bash
./tools/ogenic/install.sh --target ../my-other-project --dry-run
```

Existing files are never overwritten. Pass `--force` when you genuinely want to
replace an installed copy with a newer one. To remove it again:

```bash
./tools/ogenic/install.sh --target ../my-other-project --uninstall
```

Uninstall removes only the seven Ogenic skills and six Ogenic commands by name.
Anything else in that `.claude` directory is left alone.

## Checking it after a change

```bash
python3 tools/ogenic/validate_toolkit.py
```

Run this after editing any skill. A skill with malformed frontmatter is not a
skill that loads badly, it is a skill that does not load at all, and the failure
is silent.

## Editing the skills

The skills are opinionated on purpose, and the opinions are meant to be yours.
Edit them freely. Two rules keep them working:

1. **Keep the frontmatter valid.** `name` must be lowercase kebab-case and must
   match the directory name. `description` must say what the skill does and when
   to use it, because that sentence is the only thing Claude sees when deciding
   whether to load the body.
2. **Write the description for triggering, not for a catalogue.** Include the
   words you would actually say. "Use when Gibson asks to commit, push, open a
   PR, merge, tag or release" triggers. "Version control best practices" does
   not.

Run the validator afterwards, and add the new skill's directory name to the
`SKILLS` array in `tools/ogenic/install.sh` so it travels with the rest.

## Design notes

- **Gates produce artefacts.** You do not pass a stage by intending to, you pass
  it by writing the frame, the plan or the evidence line. That is what makes the
  workflow auditable rather than decorative.
- **Evidence over assertion.** Every skill pushes towards stating what was
  actually run and what actually came back. "Should work" is treated as a
  failure to verify, not as a report.
- **Root causes over symptoms.** The debug skill refuses the broad `except`, the
  sleep-to-fix-a-race and the special case for the one input that failed.
- **Compression, not skipping.** A typo fix runs the same five stages in ninety
  seconds. The stages never disappear, they shrink.
