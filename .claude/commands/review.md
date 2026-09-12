---
description: Review code against the Ogenic bar - correctness, failure paths, security, fit, clarity
argument-hint: [file, diff or "staged"]
---

Load the `ogenic-review` skill from `.claude/skills/ogenic-review/SKILL.md` and review:

$ARGUMENTS

If no target is given, review the working tree diff against the base branch. Run the passes in order, challenge every finding before reporting it, and rank the results by severity with file, line, failing input, cause and fix.
