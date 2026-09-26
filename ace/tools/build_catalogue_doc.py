#!/usr/bin/env python3
"""Regenerate ace/CATALOGUE.md from ace/catalogue.json.

The JSON is the single source of truth for the ACE matrix; the Markdown is a
readable view of it. Generating one from the other means they cannot drift.

    python3 ace/tools/build_catalogue_doc.py
    python3 ace/tools/build_catalogue_doc.py --check   # fail if out of date

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ACE_ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_JSON = ACE_ROOT / "catalogue.json"
CATALOGUE_DOC = ACE_ROOT / "CATALOGUE.md"


def render(data: dict) -> str:
    categories = data["categories"]
    lenses = data["lenses"]
    lines = [
        "# ACE catalogue",
        "",
        "Generated from `catalogue.json`. Do not edit by hand; edit the JSON and",
        "regenerate with `python3 ace/tools/build_catalogue_doc.py`.",
        "",
        (
            f"{len(categories)} categories x {len(lenses)} lenses = "
            f"{len(categories) * len(lenses)} engines."
        ),
        "",
        "## The seven niche lenses",
        "",
        "| Lens | Covers | Typical Gibcom client |",
        "|---|---|---|",
    ]
    for lens in lenses:
        lines.append(
            f"| **{lens['code']}** {lens['name']} | {lens['covers']} | {lens['typical']} |"
        )

    for prefix, name in data["business_lines"].items():
        lines += [
            "",
            f"## {name} ({prefix})",
            "",
            "| Code | Category | What it does |",
            "|---|---|---|",
        ]
        for category in categories:
            if category["code"].startswith(prefix):
                lines.append(
                    f"| `{category['code']}` | {category['name']} | {category['summary']} |"
                )

    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if CATALOGUE.md is out of date, without rewriting it",
    )
    args = parser.parse_args(argv)

    data = json.loads(CATALOGUE_JSON.read_text(encoding="utf-8"))
    rendered = render(data)

    if args.check:
        current = (
            CATALOGUE_DOC.read_text(encoding="utf-8") if CATALOGUE_DOC.is_file() else ""
        )
        if current == rendered:
            print("CATALOGUE.md is up to date.")
            return 0
        print(
            "CATALOGUE.md is out of date. Run: python3 ace/tools/build_catalogue_doc.py",
            file=sys.stderr,
        )
        return 1

    CATALOGUE_DOC.write_text(rendered, encoding="utf-8")
    print(
        f"CATALOGUE.md regenerated: {len(data['categories'])} categories, "
        f"{len(data['lenses'])} lenses."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
