#!/usr/bin/env python3
"""Report ACE library coverage and client programme progress.

The ACE matrix is 48 categories x 7 lenses = 336 engine briefs. At the ten a
week the generator suggests, that is roughly eight months of building, so the
useful question is never "what exists" but "where am I against 336, and what
should I build next".

    python3 ace/tools/ace_status.py                 # coverage summary
    python3 ace/tools/ace_status.py --line DM       # one business line
    python3 ace/tools/ace_status.py --lens L2       # one niche lens
    python3 ace/tools/ace_status.py --missing       # what is not built yet
    python3 ace/tools/ace_status.py --clients       # client programme progress
    python3 ace/tools/ace_status.py --matrix        # the full 48 x 7 grid

Standard library only. Reads the filesystem, writes nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ACE_ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ACE_ROOT / "catalogue.json"
LIBRARY_DIR = ACE_ROOT / "library"
CLIENTS_DIR = ACE_ROOT / "clients"

# library/[CODE]-[LENS]-[slug].md, per the generator skill.
BRIEF_PATTERN = re.compile(r"^(DM|AI|TR)(\d{2})-(L[1-7])-(.+)\.md$")


def load_catalogue() -> dict:
    return json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))


def built_engines() -> dict[tuple[str, str], str]:
    """Map (category code, lens code) to filename for every brief on disk."""
    found = {}
    if not LIBRARY_DIR.is_dir():
        return found
    for path in sorted(LIBRARY_DIR.glob("*.md")):
        match = BRIEF_PATTERN.match(path.name)
        if match:
            code = f"{match.group(1)}{match.group(2)}"
            found[(code, match.group(3))] = path.name
    return found


def bar(done: int, total: int, width: int = 24) -> str:
    if total == 0:
        return " " * width
    filled = round(width * done / total)
    return "#" * filled + "." * (width - filled)


def print_summary(catalogue: dict, built: dict) -> None:
    categories = catalogue["categories"]
    lenses = catalogue["lenses"]
    lines = catalogue["business_lines"]
    total = len(categories) * len(lenses)

    print("ACE library coverage\n")
    print(
        f"{len(built)} of {total} engine briefs built  {bar(len(built), total)}  "
        f"{len(built) / total * 100:.1f}%\n"
    )

    print("By business line")
    for prefix, name in lines.items():
        line_categories = [c for c in categories if c["code"].startswith(prefix)]
        line_total = len(line_categories) * len(lenses)
        line_done = sum(1 for (code, _) in built if code.startswith(prefix))
        print(
            f"  {prefix}  {name:<24}  {line_done:>3}/{line_total:<3}  {bar(line_done, line_total)}"
        )

    print("\nBy niche lens")
    for lens in lenses:
        lens_done = sum(1 for (_, lens_code) in built if lens_code == lens["code"])
        lens_total = len(categories)
        print(
            f"  {lens['code']}  {lens['name']:<38}  {lens_done:>3}/{lens_total:<3}  "
            f"{bar(lens_done, lens_total)}"
        )

    remaining = total - len(built)
    if remaining:
        print(
            f"\n{remaining} remaining. At ten a week that is about "
            f"{remaining / 10:.0f} week(s)."
        )


def print_matrix(catalogue: dict, built: dict) -> None:
    lenses = [lens["code"] for lens in catalogue["lenses"]]
    print("ACE matrix. X built, . not yet.\n")
    print(f"{'Code':<6} {'Category':<44} " + " ".join(lenses))
    print("-" * (6 + 45 + len(lenses) * 3))
    for category in catalogue["categories"]:
        marks = " ".join(
            " X" if (category["code"], lens) in built else " ." for lens in lenses
        )
        print(f"{category['code']:<6} {category['name'][:44]:<44} {marks}")


def print_missing(
    catalogue: dict, built: dict, line: str | None, lens_filter: str | None
) -> int:
    categories = catalogue["categories"]
    lenses = catalogue["lenses"]
    if line:
        categories = [c for c in categories if c["code"].startswith(line.upper())]
    if lens_filter:
        lenses = [
            lens for lens in lenses if lens["code"].upper() == lens_filter.upper()
        ]

    missing = [
        (category, lens)
        for category in categories
        for lens in lenses
        if (category["code"], lens["code"]) not in built
    ]
    if not missing:
        print("Nothing missing for that filter. All built.")
        return 0

    print(f"{len(missing)} engine brief(s) not built yet:\n")
    for category, lens in missing:
        print(
            f"  {category['code']}-{lens['code']}  {category['name']}  ({lens['name']})"
        )
    return len(missing)


def print_built(
    catalogue: dict, built: dict, line: str | None, lens_filter: str | None
) -> int:
    names = {c["code"]: c["name"] for c in catalogue["categories"]}
    rows = sorted(built.items())
    if line:
        rows = [row for row in rows if row[0][0].startswith(line.upper())]
    if lens_filter:
        rows = [row for row in rows if row[0][1].upper() == lens_filter.upper()]

    if not rows:
        print("No engine briefs built yet for that filter.")
        return 0

    print(f"{len(rows)} engine brief(s) built:\n")
    for (code, lens), filename in rows:
        print(f"  {code}-{lens}  {names.get(code, 'unknown category')}")
        print(f"           library/{filename}")
    return len(rows)


def print_clients() -> int:
    """Report progress for every client programme folder."""
    if not CLIENTS_DIR.is_dir():
        print("No clients directory.")
        return 0

    folders = [
        path
        for path in sorted(CLIENTS_DIR.iterdir())
        if path.is_dir() and not path.name.startswith("_")
    ]
    if not folders:
        print("No client programmes yet.")
        print("A programme folder is named '[CLIENT] - [CATEGORY CODE] - ACE'.")
        return 0

    print(f"{len(folders)} client programme(s)\n")
    for folder in folders:
        campaigns = folder / "campaigns"
        deliverables = folder / "deliverables"
        planned = (
            sorted(path.name for path in campaigns.iterdir() if path.is_dir())
            if campaigns.is_dir()
            else []
        )
        assembled = (
            sorted(path.name for path in deliverables.iterdir() if path.is_dir())
            if deliverables.is_dir()
            else []
        )
        assets = len(list(campaigns.rglob("asset-*.md"))) if campaigns.is_dir() else 0

        canon = [
            name
            for name in (
                "BRAND_VAULT.md",
                "CONTENT_LEDGER.md",
                "PRODUCTION_PROTOCOL.md",
            )
            if (folder / name).is_file()
        ]

        print(f"  {folder.name}")
        print(
            f"    canon files   {len(canon)}/3 present"
            + ("" if len(canon) == 3 else f" ({', '.join(canon) or 'none'})")
        )
        print(f"    campaigns     {len(planned)}/9 started")
        print(f"    assets        {assets}/117 written")
        print(f"    deliverables  {len(assembled)} pack(s) assembled")
        if canon and len(canon) < 3:
            print(
                "    warning: incomplete canon. The engine re-reads all three before drafting."
            )
        print()
    return len(folders)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--line", help="Filter to a business line: DM, AI or TR")
    parser.add_argument("--lens", help="Filter to a niche lens: L1 to L7")
    parser.add_argument(
        "--missing", action="store_true", help="List what is not built yet"
    )
    parser.add_argument("--built", action="store_true", help="List what is built")
    parser.add_argument(
        "--matrix", action="store_true", help="Print the full 48 x 7 grid"
    )
    parser.add_argument(
        "--clients", action="store_true", help="Report client programme progress"
    )
    args = parser.parse_args(argv)

    if args.clients:
        print_clients()
        return 0

    catalogue = load_catalogue()
    built = built_engines()

    if args.matrix:
        print_matrix(catalogue, built)
    elif args.missing:
        print_missing(catalogue, built, args.line, args.lens)
    elif args.built:
        print_built(catalogue, built, args.line, args.lens)
    elif args.line or args.lens:
        print_built(catalogue, built, args.line, args.lens)
        print()
        print_missing(catalogue, built, args.line, args.lens)
    else:
        print_summary(catalogue, built)
    return 0


def run() -> int:
    """Entry point that survives its output being piped into head or less.

    Without this, closing the pipe early raises BrokenPipeError mid-print and
    Python prints a second error while flushing at shutdown. Reporting tools
    get piped constantly, so handle it rather than let it look like a crash.
    """
    try:
        return main()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 0
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(run())
