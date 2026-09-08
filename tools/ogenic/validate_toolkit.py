#!/usr/bin/env python3
"""Validate the Ogenic God Mode toolkit.

Checks every skill and slash command in a `.claude` directory for the
structural rules the toolkit relies on: present and well formed frontmatter,
a name that matches its directory, a description that will actually trigger,
and no accidental secrets committed alongside them.

Usage:
    python tools/ogenic/validate_toolkit.py [--root .claude] [--quiet]

Exit codes:
    0  everything passed
    1  at least one error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# A description shorter than this is unlikely to trigger reliably; longer than
# this tends to get truncated in the skill listing.
MIN_DESCRIPTION = 40
MAX_DESCRIPTION = 1024
MAX_NAME = 64

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# A usable description tells the model when to reach for the skill. Accept any
# of the natural phrasings rather than insisting on one exact wording.
TRIGGER_PATTERN = re.compile(
    r"\buse (when|whenever|for|at|before|after|during|this|it)\b", re.IGNORECASE
)

SECRET_PATTERN = re.compile(
    r"(sk-[A-Za-z0-9]{16,}"
    r"|ghp_[A-Za-z0-9]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|BEGIN [A-Z ]*PRIVATE KEY)"
)


class Problem:
    """A single validation failure or warning."""

    def __init__(self, path: Path, message: str, fatal: bool = True) -> None:
        self.path = path
        self.message = message
        self.fatal = fatal

    def __str__(self) -> str:
        level = "error" if self.fatal else "warning"
        return f"{level}: {self.path}: {self.message}"


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """Return the frontmatter mapping and the body.

    Deliberately a minimal parser rather than a YAML dependency: the toolkit
    only uses flat `key: value` frontmatter, and the validator must run in CI
    without installing anything.
    """
    if not text.startswith("---"):
        return None, text

    lines = text.split("\n")
    closing = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing = index
            break
    if closing is None:
        return None, text

    fields: dict[str, str] = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key.strip()] = value

    return fields, "\n".join(lines[closing + 1 :])


def check_description(path: Path, description: str) -> list[Problem]:
    problems: list[Problem] = []
    if len(description) < MIN_DESCRIPTION:
        problems.append(
            Problem(
                path,
                f"description is only {len(description)} chars, needs {MIN_DESCRIPTION}+ to trigger reliably",
            )
        )
    if len(description) > MAX_DESCRIPTION:
        problems.append(
            Problem(
                path,
                f"description is {len(description)} chars, over the {MAX_DESCRIPTION} limit",
            )
        )
    if not TRIGGER_PATTERN.search(description):
        problems.append(
            Problem(
                path,
                "description should say when to use the skill ('Use when ...')",
                fatal=False,
            )
        )
    return problems


def validate_skill(skill_dir: Path) -> list[Problem]:
    problems: list[Problem] = []
    skill_file = skill_dir / "SKILL.md"

    if not skill_file.is_file():
        return [Problem(skill_dir, "missing SKILL.md")]

    text = skill_file.read_text(encoding="utf-8")
    fields, body = parse_frontmatter(text)

    if fields is None:
        return [Problem(skill_file, "missing or unterminated YAML frontmatter")]

    name = fields.get("name", "")
    if not name:
        problems.append(Problem(skill_file, "frontmatter is missing 'name'"))
    else:
        if not NAME_PATTERN.match(name):
            problems.append(
                Problem(skill_file, f"name '{name}' must be lowercase kebab-case")
            )
        if len(name) > MAX_NAME:
            problems.append(
                Problem(
                    skill_file, f"name is {len(name)} chars, over the {MAX_NAME} limit"
                )
            )
        if name != skill_dir.name:
            problems.append(
                Problem(
                    skill_file,
                    f"name '{name}' does not match directory '{skill_dir.name}'",
                )
            )

    description = fields.get("description", "")
    if not description:
        problems.append(Problem(skill_file, "frontmatter is missing 'description'"))
    else:
        problems.extend(check_description(skill_file, description))

    if not body.strip():
        problems.append(Problem(skill_file, "body is empty"))
    elif not re.search(r"^# .+", body, re.MULTILINE):
        problems.append(
            Problem(skill_file, "body has no top-level heading", fatal=False)
        )

    return problems


def validate_command(command_file: Path) -> list[Problem]:
    problems: list[Problem] = []
    text = command_file.read_text(encoding="utf-8")
    fields, body = parse_frontmatter(text)

    if fields is None:
        problems.append(
            Problem(
                command_file, "missing frontmatter with a 'description'", fatal=False
            )
        )
        body = text
    elif not fields.get("description"):
        problems.append(
            Problem(command_file, "frontmatter is missing 'description'", fatal=False)
        )

    if not body.strip():
        problems.append(Problem(command_file, "body is empty"))

    return problems


def scan_for_secrets(paths: list[Path]) -> list[Problem]:
    problems: list[Problem] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(text.split("\n"), start=1):
            if SECRET_PATTERN.search(line):
                problems.append(
                    Problem(path, f"line {number} looks like a real credential")
                )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Ogenic God Mode toolkit."
    )
    parser.add_argument(
        "--root", default=".claude", help="toolkit root (default: .claude)"
    )
    parser.add_argument("--quiet", action="store_true", help="only print problems")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 1

    problems: list[Problem] = []
    checked: list[Path] = []

    skills_dir = root / "skills"
    skills = (
        sorted(p for p in skills_dir.iterdir() if p.is_dir())
        if skills_dir.is_dir()
        else []
    )
    if not skills:
        problems.append(Problem(skills_dir, "no skills found"))
    for skill_dir in skills:
        problems.extend(validate_skill(skill_dir))
        checked.append(skill_dir / "SKILL.md")

    commands_dir = root / "commands"
    commands = sorted(commands_dir.glob("*.md")) if commands_dir.is_dir() else []
    for command_file in commands:
        problems.extend(validate_command(command_file))
        checked.append(command_file)

    problems.extend(scan_for_secrets([p for p in checked if p.is_file()]))

    errors = [p for p in problems if p.fatal]
    warnings = [p for p in problems if not p.fatal]

    for problem in errors + warnings:
        print(str(problem), file=sys.stderr if problem.fatal else sys.stdout)

    if not args.quiet:
        print(f"\nchecked {len(skills)} skills and {len(commands)} commands")
        print(f"{len(errors)} error(s), {len(warnings)} warning(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
