#!/usr/bin/env python3
"""Import AIBOS conversations from a Claude data export into aibos/conversations/.

Claude does not expose past conversations to an agent session, so the only way
to gather existing chat history is to export it yourself and import it here.

Request the export from Claude: Settings, then Privacy, then Export data. Claude
emails a zip. Unzip it and point this script at the conversations.json inside.

    python3 aibos/tools/import_claude_export.py path/to/conversations.json

By default it keeps only conversations whose title or body mentions one of the
match terms below, writes one Markdown file per conversation into
aibos/conversations/, and regenerates aibos/INDEX.md.

Standard library only. Nothing leaves your machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_TERMS = ["aibos", "command centre", "command center", "gibcom"]

REPO_ROOT = Path(__file__).resolve().parents[2]
CONVERSATIONS_DIR = REPO_ROOT / "aibos" / "conversations"
INDEX_PATH = REPO_ROOT / "aibos" / "INDEX.md"


def slugify(text: str, max_length: int = 60) -> str:
    """Turn a conversation title into a safe, readable filename fragment."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0]
    return slug or "untitled"


def parse_date(value: str | None) -> str:
    """Return an ISO date from a Claude timestamp, or a placeholder."""
    if not value:
        return "0000-00-00"
    cleaned = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned).date().isoformat()
    except ValueError:
        return value[:10] if len(value) >= 10 else "0000-00-00"


def message_text(message: dict) -> str:
    """Extract text from a message, handling both export shapes."""
    text = (message.get("text") or "").strip()
    if text:
        return text
    parts = []
    for block in message.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append((block.get("text") or "").strip())
    return "\n\n".join(part for part in parts if part)


def conversation_matches(conversation: dict, terms: list[str]) -> bool:
    haystack = (conversation.get("name") or "").lower()
    for message in conversation.get("chat_messages") or []:
        haystack += "\n" + message_text(message).lower()
    return any(term in haystack for term in terms)


def render(conversation: dict) -> str:
    """Render one conversation as a Markdown file with frontmatter."""
    title = (conversation.get("name") or "Untitled conversation").strip()
    created = parse_date(conversation.get("created_at"))
    updated = parse_date(conversation.get("updated_at"))
    uuid = conversation.get("uuid", "")

    lines = [
        "---",
        f"title: {json.dumps(title)}",
        f"date: {created}",
        f"updated: {updated}",
        "source: claude-web",
        "topics: []",
        "status: active",
        f"claude_uuid: {uuid}",
        "imported: true",
        "---",
        "",
        f"# {title}",
        "",
        "> Imported from a Claude data export. The summary sections below are",
        "> empty on purpose. Fill them in, then the transcript becomes optional",
        "> reading rather than required reading.",
        "",
        "## What we were trying to do",
        "",
        "_To fill in._",
        "",
        "## What was decided",
        "",
        "_To fill in._",
        "",
        "## Open threads",
        "",
        "_To fill in._",
        "",
        "## Transcript",
        "",
    ]

    for message in conversation.get("chat_messages") or []:
        body = message_text(message)
        if not body:
            continue
        sender = message.get("sender", "unknown")
        speaker = "Gibson" if sender == "human" else "Claude"
        lines.append(f"### {speaker}")
        lines.append("")
        lines.append(body)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_index() -> int:
    """Regenerate INDEX.md from the frontmatter of every conversation file."""
    rows = []
    for path in sorted(CONVERSATIONS_DIR.glob("*.md"), reverse=True):
        if path.name.startswith("_") or path.name == "README.md":
            continue
        meta = {}
        with path.open(encoding="utf-8") as handle:
            if handle.readline().strip() != "---":
                continue
            for line in handle:
                if line.strip() == "---":
                    break
                if ":" in line:
                    key, _, value = line.partition(":")
                    meta[key.strip()] = value.strip().strip('"')
        rows.append(
            (
                meta.get("date", "unknown"),
                meta.get("title", path.stem),
                meta.get("topics", "[]"),
                meta.get("status", "unknown"),
                path.name,
            )
        )

    lines = [
        "# AIBOS conversation index",
        "",
        "Generated by `tools/import_claude_export.py`. Do not edit by hand;",
        "edit the frontmatter of the conversation files and regenerate.",
        "",
        f"{len(rows)} conversation(s) captured.",
        "",
        "| Date | Title | Topics | Status |",
        "|---|---|---|---|",
    ]
    for date, title, topics, status, filename in rows:
        safe_title = title.replace("|", "\\|")
        lines.append(
            f"| {date} | [{safe_title}](conversations/{filename}) | {topics} | {status} |"
        )
    if not rows:
        lines.append("| | _Nothing captured yet_ | | |")
    lines.append("")

    INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "export", type=Path, nargs="?", help="Path to conversations.json"
    )
    parser.add_argument(
        "--term",
        action="append",
        dest="terms",
        help="Match term, repeatable. Defaults to AIBOS related terms.",
    )
    parser.add_argument(
        "--all", action="store_true", help="Import every conversation, no filter"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Report what would be written"
    )
    parser.add_argument(
        "--index-only",
        action="store_true",
        help="Skip importing and just regenerate INDEX.md",
    )
    args = parser.parse_args()

    if args.index_only:
        count = write_index()
        print(f"Index regenerated: {count} conversation(s).")
        return 0

    if args.export is None:
        parser.error("an export path is required unless --index-only is used")

    if not args.export.is_file():
        print(f"No such file: {args.export}", file=sys.stderr)
        return 1

    try:
        data = json.loads(args.export.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"Could not parse {args.export} as JSON: {error}", file=sys.stderr)
        return 1

    if not isinstance(data, list):
        print(
            "Expected conversations.json to contain a list of conversations.",
            file=sys.stderr,
        )
        return 1

    terms = [term.lower() for term in (args.terms or DEFAULT_TERMS)]
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)

    written = skipped = 0
    for conversation in data:
        if not args.all and not conversation_matches(conversation, terms):
            skipped += 1
            continue

        date = parse_date(conversation.get("created_at"))
        slug = slugify(conversation.get("name") or "untitled")
        path = CONVERSATIONS_DIR / f"{date}-{slug}.md"

        suffix = 2
        while path.exists() and args.dry_run is False:
            path = CONVERSATIONS_DIR / f"{date}-{slug}-{suffix}.md"
            suffix += 1

        if args.dry_run:
            print(f"would write {path.relative_to(REPO_ROOT)}")
        else:
            path.write_text(render(conversation), encoding="utf-8")
        written += 1

    if args.dry_run:
        print(f"\nDry run: {written} to import, {skipped} filtered out.")
        return 0

    count = write_index()
    print(f"Imported {written} conversation(s), filtered out {skipped}.")
    print(f"Index regenerated: {count} entry/entries in aibos/INDEX.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
