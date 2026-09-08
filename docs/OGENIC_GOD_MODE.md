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
| `ogenic-god-mode` | The router. Sends each request to the skill that owns it, and sets the non-negotiables |
| `ogenic-code-workflow` | The five stages, the gates, the verification ladder and the definition of done |
| `ogenic-secure` | This repository's secret and input rules, plus the recovery procedure for a committed credential |
| `ogenic-ship` | The pre-push gate, commit message format and PR conventions |

### Why only four

An earlier version shipped seven, and three of them restated doctrine that the
account-level skills already own better. `ogenic-debug` duplicated
`systematic-debugging`, `ogenic-review` duplicated `code-review` and its
siblings, and `ogenic-scaffold` duplicated `brainstorming`. Two competing
doctrines meant Claude sometimes loaded one, sometimes the other, occasionally
both with conflicting advice.

They are gone. The router now names the account-level skill for each concern and
reaches for an Ogenic skill only where this repository adds something: the house
stages and gates, the rules that come from this app handling a user's API key,
and the pre-push gate. `ogenic-scaffold`'s one genuinely local idea, finding the
existing pattern before writing, moved into the workflow's Frame stage.

Where an account skill and an Ogenic skill disagree, the Ogenic skill wins inside
this repository, because it encodes decisions made here.

Skills load on demand. Claude reads the description in each file's frontmatter
and pulls in the body only when the task matches, so having seven installed
costs nothing until one is needed.

### Slash commands, in `.claude/commands/`

| Command | Runs |
|---|---|
| `/god-mode <task>` | Route the task and set the posture |
| `/build <change>` | The full five-stage code workflow |
| `/secure <target>` | The security pass |
| `/ship` | Pre-push gate, commit, push, draft PR |

For debugging and code review, use the account-level skills and the built-in
`/code-review` and `/security-review` commands. Ogenic does not wrap them.

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
- **verify** compiles all Python, runs `ruff check` and `ruff format --check`
  across the repository, then runs the test suite.
- **secrets** scans every tracked file for credential patterns and fails the
  build on a hit. The validator, the workflow, `.claude` and the two test files
  that assert the scanners fire are excluded, because they carry those patterns
  on purpose. Every other file, new test files included, stays in scope.

## Using it

In a Claude Code session in this repository, the skills are picked up
automatically. Start with the router:

```
/god-mode add a model picker to the sidebar
```

Or go straight to a stage:

```
/build add streaming error handling to the chat loop
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

Uninstall removes only the four Ogenic skills and four Ogenic commands by name.
Anything else in that `.claude` directory is left alone.

## Checking it after a change

```bash
python3 tools/ogenic/validate_toolkit.py
python3 -m unittest discover -s tests -t .
```

Run these after editing any skill or the validator. A skill with malformed frontmatter is not a
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
