#!/usr/bin/env python3
"""Import AIBOS conversations from an AI chat export into aibos/conversations/.

Neither Claude nor ChatGPT exposes past conversations to an agent session, so
the only way to gather existing chat history is to export it yourself and import
it here. Both vendors' export formats are supported and detected automatically.

Claude: Settings, then Privacy, then Export data. Claude emails a zip; the file
you want is conversations.json.

ChatGPT: Settings, then Data controls, then Export data. Same filename.

    python3 aibos/tools/import_chat_export.py path/to/conversations.json

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
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_TERMS = ["aibos", "command centre", "command center", "gibcom"]

REPO_ROOT = Path(__file__).resolve().parents[2]
CONVERSATIONS_DIR = REPO_ROOT / "aibos" / "conversations"
INDEX_PATH = REPO_ROOT / "aibos" / "INDEX.md"

UNKNOWN_DATE = "0000-00-00"

SPEAKERS = {"human": "Gibson", "user": "Gibson", "assistant": "Claude"}


# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------


def slugify(text: str, max_length: int = 60) -> str:
    """Turn a conversation title into a safe, readable filename fragment."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0]
    return slug or "untitled"


def parse_date(value: object) -> str:
    """Return an ISO date from either an ISO string or a Unix timestamp."""
    if value is None or value == "":
        return UNKNOWN_DATE
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc).date().isoformat()
        except (OverflowError, OSError, ValueError):
            return UNKNOWN_DATE
    if isinstance(value, str):
        try:
            return (
                datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
            )
        except ValueError:
            return value[:10] if len(value) >= 10 else UNKNOWN_DATE
    return UNKNOWN_DATE


# --------------------------------------------------------------------------
# Format detection and normalisation
#
# Both vendors ship a file called conversations.json with entirely different
# shapes. Everything below converts one of them into a single internal record:
#
#     {"uuid", "title", "created", "updated", "source", "messages": [...]}
#
# so that filtering and rendering only ever deal with one shape.
# --------------------------------------------------------------------------


def detect_format(data: list) -> str:
    """Return "claude", "chatgpt" or "unknown" for a parsed export."""
    for conversation in data:
        if not isinstance(conversation, dict):
            continue
        if "chat_messages" in conversation:
            return "claude"
        if "mapping" in conversation:
            return "chatgpt"
    return "unknown"


def claude_message_text(message: dict) -> str:
    """Extract text from a Claude message, handling both of its shapes."""
    text = (message.get("text") or "").strip()
    if text:
        return text
    parts = []
    for block in message.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append((block.get("text") or "").strip())
    return "\n\n".join(part for part in parts if part)


def normalise_claude(conversation: dict) -> dict:
    messages = []
    for message in conversation.get("chat_messages") or []:
        body = claude_message_text(message)
        if body:
            messages.append({"role": message.get("sender", "unknown"), "text": body})
    return {
        "uuid": conversation.get("uuid", ""),
        "title": (conversation.get("name") or "Untitled conversation").strip(),
        "created": parse_date(conversation.get("created_at")),
        "updated": parse_date(conversation.get("updated_at")),
        "source": "claude-web",
        "messages": messages,
    }


def chatgpt_message_text(message: dict) -> str:
    """Extract text from a ChatGPT message node."""
    content = message.get("content") or {}
    if content.get("content_type") not in (None, "text", "multimodal_text"):
        return ""
    parts = []
    for part in content.get("parts") or []:
        if isinstance(part, str) and part.strip():
            parts.append(part.strip())
    return "\n\n".join(parts)


def chatgpt_ordered_nodes(mapping: dict, current_node: str | None) -> list[dict]:
    """Return the conversation's message nodes in order.

    ChatGPT stores a tree, because edited prompts create branches. Walking back
    from current_node gives the branch actually left on screen. Where that
    pointer is missing, fall back to ordering every node by timestamp.
    """
    if current_node and current_node in mapping:
        chain = []
        seen = set()
        node_id = current_node
        while node_id and node_id in mapping and node_id not in seen:
            seen.add(node_id)
            chain.append(mapping[node_id])
            node_id = mapping[node_id].get("parent")
        return list(reversed(chain))

    nodes = [
        node
        for node in mapping.values()
        if isinstance(node, dict) and node.get("message")
    ]
    return sorted(nodes, key=lambda node: node["message"].get("create_time") or 0)


def normalise_chatgpt(conversation: dict) -> dict:
    mapping = conversation.get("mapping") or {}
    messages = []
    for node in chatgpt_ordered_nodes(mapping, conversation.get("current_node")):
        message = node.get("message")
        if not isinstance(message, dict):
            continue
        role = (message.get("author") or {}).get("role", "unknown")
        if role == "system":
            continue
        metadata = message.get("metadata") or {}
        if metadata.get("is_visually_hidden_from_conversation"):
            continue
        body = chatgpt_message_text(message)
        if body:
            messages.append({"role": role, "text": body})

    return {
        "uuid": conversation.get("conversation_id") or conversation.get("id") or "",
        "title": (conversation.get("title") or "Untitled conversation").strip(),
        "created": parse_date(conversation.get("create_time")),
        "updated": parse_date(conversation.get("update_time")),
        "source": "chatgpt",
        "messages": messages,
    }


def normalise(data: list, export_format: str) -> list[dict]:
    normaliser = normalise_claude if export_format == "claude" else normalise_chatgpt
    return [normaliser(item) for item in data if isinstance(item, dict)]


# --------------------------------------------------------------------------
# Filtering and rendering
# --------------------------------------------------------------------------


def matches(record: dict, terms: list[str]) -> bool:
    haystack = record["title"].lower()
    for message in record["messages"]:
        haystack += "\n" + message["text"].lower()
    return any(term in haystack for term in terms)


def render(record: dict) -> str:
    """Render one normalised conversation as Markdown with frontmatter."""
    lines = [
        "---",
        f"title: {json.dumps(record['title'])}",
        f"date: {record['created']}",
        f"updated: {record['updated']}",
        f"source: {record['source']}",
        "topics: []",
        "status: active",
        f"export_id: {record['uuid']}",
        "imported: true",
        "---",
        "",
        f"# {record['title']}",
        "",
        "> Imported from a chat export. The summary sections below are empty on",
        "> purpose. Fill them in, then the transcript becomes optional reading",
        "> rather than required reading.",
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

    assistant = "ChatGPT" if record["source"] == "chatgpt" else "Claude"
    for message in record["messages"]:
        role = message["role"]
        speaker = (
            "ChatGPT"
            if role == "assistant" and assistant == "ChatGPT"
            else SPEAKERS.get(role, role)
        )
        lines.append(f"### {speaker}")
        lines.append("")
        lines.append(message["text"])
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def captured_files() -> list[Path]:
    """Every captured conversation file, newest first. Templates excluded."""
    return [
        path
        for path in sorted(CONVERSATIONS_DIR.glob("*.md"), reverse=True)
        if not path.name.startswith("_") and path.name != "README.md"
    ]


def read_frontmatter(path: Path) -> dict:
    """Read a conversation file's YAML frontmatter into a flat dict.

    Deliberately not a YAML parser. The frontmatter this tool writes is flat
    `key: value` pairs, and keeping the reader trivial means the archive stays
    readable with no dependency to install.
    """
    meta = {}
    with path.open(encoding="utf-8") as handle:
        if handle.readline().strip() != "---":
            return meta
        for line in handle:
            if line.strip() == "---":
                break
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip().strip('"')
    return meta


def index_rows() -> list[tuple]:
    """Return one row per captured conversation, newest first."""
    rows = []
    for path in captured_files():
        meta = read_frontmatter(path)
        if not meta:
            continue
        rows.append(
            (
                meta.get("date", "unknown"),
                meta.get("title", path.stem),
                meta.get("topics", "[]"),
                meta.get("status", "unknown"),
                meta.get("source", "unknown"),
                path.name,
            )
        )
    return rows


def write_index() -> int:
    """Regenerate INDEX.md from the frontmatter of every conversation file."""
    rows = index_rows()

    lines = [
        "# AIBOS conversation index",
        "",
        "Generated by `tools/import_chat_export.py`. Do not edit by hand;",
        "edit the frontmatter of the conversation files and regenerate.",
        "",
        f"{len(rows)} conversation(s) captured.",
        "",
        "| Date | Title | Topics | Status | Source |",
        "|---|---|---|---|---|",
    ]
    for date, title, topics, status, source, filename in rows:
        safe_title = title.replace("|", "\\|")
        lines.append(
            f"| {date} | [{safe_title}](conversations/{filename}) "
            f"| {topics} | {status} | {source} |"
        )
    if not rows:
        lines.append("| | _Nothing captured yet_ | | | |")
    lines.append("")

    INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
    return len(rows)


def list_conversations(source: str | None = None, topic: str | None = None) -> int:
    """Print the captured archive as a table. Returns the number of rows shown."""
    rows = index_rows()
    if source:
        rows = [row for row in rows if row[4].lower() == source.lower()]
    if topic:
        rows = [row for row in rows if topic.lower() in row[2].lower()]

    if not rows:
        print(
            "Nothing captured yet."
            if not (source or topic)
            else "No conversations match that filter."
        )
        return 0

    widths = [
        max(
            len(str(row[index]))
            for row in [*rows, ("Date", "", "Topics", "Status", "Source", "")]
        )
        for index in (0, 2, 3, 4)
    ]
    header = (
        f"{'Date':<{widths[0]}}  {'Source':<{widths[3]}}  "
        f"{'Status':<{widths[2]}}  {'Topics':<{widths[1]}}  Title"
    )
    print(header)
    print("-" * len(header))
    for date, title, topics, status, source_value, _ in rows:
        print(
            f"{date:<{widths[0]}}  {source_value:<{widths[3]}}  "
            f"{status:<{widths[2]}}  {topics:<{widths[1]}}  {title}"
        )
    print(f"\n{len(rows)} conversation(s).")
    return len(rows)


def search_conversations(term: str, context: int = 0) -> int:
    """Print every captured line matching a term. Returns the match count."""
    needle = term.lower()
    matches = 0
    for path in captured_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        hits = [index for index, line in enumerate(lines) if needle in line.lower()]
        if not hits:
            continue

        meta = read_frontmatter(path)
        title = meta.get("title", path.stem)
        print(
            f"\n{path.name}  ({meta.get('source', 'unknown')}, {meta.get('date', 'unknown')})"
        )
        print(f"  {title}")
        previous_end = None
        for index in hits:
            start = max(0, index - context)
            end = min(len(lines), index + context + 1)
            # Mark a jump so two separate blocks never read as continuous text.
            if previous_end is not None and start > previous_end:
                print("      ...")
            for line_number in range(max(start, previous_end or 0), end):
                marker = ">" if line_number == index else " "
                print(f"  {marker} {line_number + 1:>4}: {lines[line_number].strip()}")
            previous_end = end
            matches += 1

    if matches:
        print(f"\n{matches} match(es) for {term!r}.")
    else:
        print(
            f"No matches for {term!r} in {len(captured_files())} captured conversation(s)."
        )
    return matches


def unique_path(directory: Path, date: str, slug: str) -> Path:
    """Return a path that does not collide with an existing file."""
    path = directory / f"{date}-{slug}.md"
    suffix = 2
    while path.exists():
        path = directory / f"{date}-{slug}-{suffix}.md"
        suffix += 1
    return path


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
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
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_only",
        help="List what has been captured, newest first, and exit",
    )
    parser.add_argument(
        "--search",
        metavar="TERM",
        help="Search captured conversations for a term and exit",
    )
    parser.add_argument(
        "--source",
        help="With --list, show only this source (claude-web, chatgpt, claude-code)",
    )
    parser.add_argument(
        "--topic",
        help="With --list, show only conversations whose topics contain this",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=0,
        metavar="N",
        help="With --search, show N lines either side of each match",
    )
    args = parser.parse_args(argv)

    if args.list_only:
        list_conversations(source=args.source, topic=args.topic)
        return 0

    if args.search:
        search_conversations(args.search, context=args.context)
        return 0

    if args.index_only:
        print(f"Index regenerated: {write_index()} conversation(s).")
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

    export_format = detect_format(data)
    if export_format == "unknown":
        print(
            "Could not recognise this export. Expected a Claude export\n"
            "(chat_messages) or a ChatGPT export (mapping).\n"
            "Is this the right conversations.json?",
            file=sys.stderr,
        )
        return 1

    print(f"Detected a {export_format} export with {len(data)} conversation(s).")

    terms = [term.lower() for term in (args.terms or DEFAULT_TERMS)]
    records = normalise(data, export_format)

    if not args.dry_run:
        CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)

    written = skipped = empty = 0
    for record in records:
        if not args.all and not matches(record, terms):
            skipped += 1
            continue
        if not record["messages"]:
            empty += 1
            continue

        slug = slugify(record["title"])
        if args.dry_run:
            print(f"would write {record['created']}-{slug}.md")
        else:
            path = unique_path(CONVERSATIONS_DIR, record["created"], slug)
            path.write_text(render(record), encoding="utf-8")
        written += 1

    tail = f", {empty} skipped as empty" if empty else ""
    if args.dry_run:
        print(f"\nDry run: {written} to import, {skipped} filtered out{tail}.")
        return 0

    print(f"Imported {written} conversation(s), filtered out {skipped}{tail}.")
    print(f"Index regenerated: {write_index()} entry/entries in aibos/INDEX.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
