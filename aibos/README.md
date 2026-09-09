# Gibcom AIBOS Command Centre

The single project folder for everything to do with the Gibcom AIBOS Command
Centre: conversations, decisions, knowledge and the tooling that keeps them in
one place.

Owner: Gibson Nyendwa, Gibcom Marketing Support Ltd.

## Why this folder exists

Work on AIBOS has been spread across many separate chat sessions. Each session
starts cold, so context is re-explained, decisions get made twice, and nothing
accumulates. This folder is the durable home for that context. Chats are
transient. This folder is not.

## Layout

| Path | Holds |
|---|---|
| `conversations/` | One Markdown file per captured chat, newest first by date prefix |
| `decisions/` | Decisions that are settled, with the reasoning behind them |
| `knowledge/` | Stable reference: architecture, providers, conventions, glossary |
| `tools/` | The importer that turns a Claude data export into `conversations/` |
| `INDEX.md` | Generated master index of every captured conversation |

## The two ways content gets in here

**1. Bulk import of existing history.** Export your Claude data, then run the
importer. It filters the export down to AIBOS conversations and writes one
Markdown file per chat plus a regenerated index. See `tools/README.md`.

**2. Ongoing capture.** At the end of a working session that produced anything
worth keeping, copy `conversations/_TEMPLATE.md`, fill it in, commit it. Two
minutes at the end of a session, and the next session starts warm.

## Getting at what is in here

Four ways, depending on what you are doing.

**1. Browse the whole archive.**

```bash
python3 aibos/tools/import_chat_export.py --list
```

One row per captured conversation, newest first, showing date, source, status,
topics and title. Narrow it with `--source chatgpt`, `--source claude-web` or
`--topic leadgen`. The filters combine.

**2. Search across everything, whichever tool it came from.**

```bash
python3 aibos/tools/import_chat_export.py --search "ElevenLabs"
python3 aibos/tools/import_chat_export.py --search "briefing" --context 2
```

Searches every captured file regardless of source, and prints the filename,
title, line number and matching line. `--context N` shows N lines either side.
This is the one that pays off once the archive is large: it answers "where did
we discuss this" without you remembering which tool you used at the time.

**3. Read `INDEX.md`.** The same inventory as `--list`, but as a Markdown table
with links, so it renders on GitHub and in any Markdown viewer. Regenerate it
after editing frontmatter with `--index-only`.

**4. Open the files.** They are plain Markdown in `conversations/`, named
`YYYY-MM-DD-slug.md`. Any editor, `grep`, or Obsidian pointed at this folder
will work. Nothing here is locked in a database.

## How to use it in a new session

Point Claude at this folder at the start of the session:

> Read `aibos/README.md`, `aibos/INDEX.md` and anything in `aibos/knowledge/`
> before we start. We are continuing the AIBOS Command Centre work.

That replaces re-explaining the project every time.

## Related

The `gibcom-aibos-keys` and `gibcom-aibos-leadgen` skills cover credentials and
the Companies House lead-generation module. Anything decided while using them
belongs in `decisions/`.
