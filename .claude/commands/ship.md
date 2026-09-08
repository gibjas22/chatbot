---
description: Run the Ogenic pre-push gate, then commit, push and open a draft PR
argument-hint: [optional commit subject]
---

Load the `ogenic-ship` skill from `.claude/skills/ogenic-ship/SKILL.md`.

$ARGUMENTS

Run the pre-push gate in full before anything is pushed: read the staged diff line by line, scan for secrets, confirm no debug leftovers, and confirm lint and tests. Write a commit message whose subject says what and whose body says why. Push with `git push -u origin <branch>` and open the pull request as a draft, using the repository template if one exists.
