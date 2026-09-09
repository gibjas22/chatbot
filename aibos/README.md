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

## How to use it in a new session

Point Claude at this folder at the start of the session:

> Read `aibos/README.md`, `aibos/INDEX.md` and anything in `aibos/knowledge/`
> before we start. We are continuing the AIBOS Command Centre work.

That replaces re-explaining the project every time.

## Related

The `gibcom-aibos-keys` and `gibcom-aibos-leadgen` skills cover credentials and
the Companies House lead-generation module. Anything decided while using them
belongs in `decisions/`.
