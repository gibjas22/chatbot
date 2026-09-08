---
description: Run the Ogenic security pass - secrets, input handling, dependencies, data exposure
argument-hint: [file, directory or "staged"]
---

Load the `ogenic-secure` skill from `.claude/skills/ogenic-secure/SKILL.md` and run the security pass over:

$ARGUMENTS

If no target is given, scan the staged diff and the working tree. Run the secret scan, check every external input for a validation point, check every network call for a timeout and a handled failure, and work the pre-deploy checklist. Report findings with the concrete exposure, not a generic warning.
