---
description: Debug systematically - reproduce, isolate, hypothesise, fix the root cause, prove it
argument-hint: [the symptom or error]
---

Load the `ogenic-debug` skill from `.claude/skills/ogenic-debug/SKILL.md` and work this failure:

$ARGUMENTS

Reproduce before theorising. State each hypothesis as one falsifiable sentence with a mechanism. Fix where the wrong behaviour originates, not where it surfaced, then prove it with the original reproduction and a regression test. Respect the time boxes and report dead ends rather than looping.
