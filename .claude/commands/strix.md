---
description: Run the Strix safety scan - credentials, injection-prone code, risky files, debug leftovers
argument-hint: [staged (default), all, or a git range such as origin/main..HEAD]
---

Load the `strix` skill from `.claude/skills/strix/SKILL.md`, then run the scanner over:

$ARGUMENTS

Default to the staged diff when no target is given.

```bash
bash .claude/skills/strix/scripts/scan.sh            # staged
bash .claude/skills/strix/scripts/scan.sh --all      # whole tree
bash .claude/skills/strix/scripts/scan.sh --range origin/main..HEAD
```

Report every finding with its severity, the file and line, the concrete failure scenario and the
fix. Say plainly which findings are false positives and why, rather than leaving Gibson to judge
a raw list. If a real credential is found, the first instruction is to rotate it at the provider,
not to delete the line.
