---
name: ogenic-scaffold
description: "Start new code well: new files, modules, endpoints, pages, services, tests and repositories. Use when Gibson asks to create, scaffold, set up, bootstrap or start something new. Covers finding the existing pattern, the minimum viable structure, and the anti-patterns that make new code age badly."
---

# Ogenic Scaffold

New code is where a codebase either stays coherent or starts to fragment. The first version sets the pattern everyone copies, so get it boring and get it right.

## Step 1: Find the pattern that already exists

Before creating anything, find the nearest existing example and read it fully.

```bash
ls                                  # what shape is this repository?
find . -name "*.py" -not -path "./.git/*" | head -30
grep -rl "<the thing nearest to yours>" --include="*.py" .
```

Ask:

- Where does this kind of file live here?
- What is it named? Follow the local convention, even where you would have chosen differently.
- How does it get wired in: imported, registered, auto-discovered?
- How is the nearest equivalent tested?

Matching an imperfect existing pattern beats introducing a second, better one. Two patterns is worse than one mediocre pattern, because now every future contributor has to choose.

If there is genuinely no precedent, you are setting it. Say so explicitly, and keep it as plain as possible.

## Step 2: Minimum viable structure

Create the smallest thing that works and can be run. Not a framework. Not a folder tree with empty placeholder files.

For a new module:

- The module itself, with one real function that does one real thing.
- Its test, with one real case, not a placeholder assertion.
- The wiring that makes it reachable from the application.

That is it. Structure is added when the code demands it, not in advance.

## Step 3: Wire it in immediately

An unreachable file is not progress. Before adding a second function, prove the first one is called from the running application. Import it, route to it, render it, then run the app and see it work.

Code that has never executed is a guess.

## Anti-patterns

| Do not | Because |
|---|---|
| Create an abstract base class for one implementation | The right abstraction only becomes visible with the second and third case |
| Add a config option nothing sets | Every option is a permanent branch you must test forever |
| Create empty `utils.py`, `helpers.py`, `common.py` | They become junk drawers within a month. Name modules for what they do |
| Scaffold a folder tree of empty files | It looks like progress and is a map of work nobody has done |
| Copy a whole file to change three lines | You have just duplicated every bug in it. Extract or import instead |
| Add a dependency for a twenty-line job | A transitive tree you have not read, forever |
| Write a `TODO` instead of the code | Either it matters now, or it does not go in |

## New repository checklist

When starting a project rather than a file:

- [ ] `README.md` that says what it is, how to run it, and how to run the tests. Written for someone who has never seen it.
- [ ] `.gitignore` covering the language, the tooling, `.env` and local artefacts, before the first commit.
- [ ] Dependency manifest with pinned versions.
- [ ] One real test and the command that runs it.
- [ ] A linter and formatter, configured, with the command in the README.
- [ ] `LICENSE`, if it will be shared.
- [ ] CI that runs the lint and test commands on every push.
- [ ] The first commit is a working skeleton, not an empty tree.

## Naming

- Modules and files: lowercase, what it does, no filler. `chat_history.py`, not `chat_history_manager_utils.py`.
- Functions: verb phrases. `load_messages`, not `messages_loader`.
- Booleans: read as a question. `is_ready`, `has_key`, `should_retry`.
- Constants: uppercase, named for meaning rather than value. `MAX_RETRIES = 3`, never a bare `3`.
- Avoid abbreviations that are not universal in the domain. Typing is cheap, misreading is not.

## Handing off

A newly scaffolded thing is done when a colleague can find it, run it, and change it without asking you a question. If any of those three needs you present, the scaffold is not finished.
