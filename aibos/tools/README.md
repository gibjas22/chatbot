# Tools

## `import_chat_export.py`

Turns an AI chat export into `../conversations/` files plus a regenerated
`../INDEX.md`. Standard library only, nothing leaves your machine.

Both Claude and ChatGPT exports are supported, and the format is detected
automatically. Confusingly, both vendors call the file `conversations.json`
while using entirely different structures inside it, so the script sniffs for
`chat_messages` (Claude) or `mapping` (ChatGPT) and refuses anything it does not
recognise rather than writing nonsense.

### Getting the export

Neither vendor lets an agent session read your past conversations, so the
history has to come from an export you request yourself.

| Vendor | Where |
|---|---|
| Claude | Settings, then Privacy, then Export data |
| ChatGPT | Settings, then Data controls, then Export data |

Both email you a download link, usually within a few minutes. **Point the
importer straight at the downloaded zip; there is no need to unzip it.** It
finds `conversations.json` inside, whatever else the archive contains. A plain
`conversations.json` works too if you have already extracted one.

### Running it

```bash
# Straight from the downloaded zip, no unzipping
python3 aibos/tools/import_chat_export.py ~/Downloads/chatgpt-export.zip --dry-run
python3 aibos/tools/import_chat_export.py ~/Downloads/chatgpt-export.zip

# Or from an extracted conversations.json
python3 aibos/tools/import_chat_export.py ~/Downloads/export/conversations.json

# Widen or narrow the filter
python3 aibos/tools/import_chat_export.py conversations.json --term aibos --term "voice layer"

# Import everything, no filtering
python3 aibos/tools/import_chat_export.py conversations.json --all

# Rebuild the index after editing frontmatter by hand
python3 aibos/tools/import_chat_export.py --index-only
```

Run it once per vendor if you use both. The second run adds to the folder rather
than replacing it, and a filename collision gets a numeric suffix rather than
overwriting anything.

By default it keeps conversations mentioning `aibos`, `command centre`,
`command center` or `gibcom` in the title or body. Run `--dry-run` first to
check the filter catches what you expect before writing dozens of files.

### A note on ChatGPT branches

ChatGPT stores each conversation as a tree, because editing a prompt creates a
branch rather than replacing it. The importer walks back from `current_node` to
capture the branch actually left on screen, which is what you remember having.
Where that pointer is missing it falls back to ordering every message by
timestamp. System messages and hidden messages are dropped either way.

### Reading the archive back

Importing is only half of it. These read the folder rather than writing to it:

```bash
# Everything captured, newest first
python3 aibos/tools/import_chat_export.py --list

# Just one source, or one topic
python3 aibos/tools/import_chat_export.py --list --source chatgpt
python3 aibos/tools/import_chat_export.py --list --topic leadgen

# Search across every conversation, whatever tool it came from
python3 aibos/tools/import_chat_export.py --search "ElevenLabs"
python3 aibos/tools/import_chat_export.py --search "briefing" --context 2
```

`--search` is the one that matters once the archive grows past what you can
hold in your head. It reports the filename, title, line number and matching
line, and does not care whether the conversation started in Claude or ChatGPT.

### After importing

The importer cannot summarise for you, so each imported file has empty summary
sections above the transcript. Work through them and fill in what the session
was for, what was decided and what is still open. Set `topics` and `status` in
the frontmatter while you are there, then rerun with `--index-only`.

That pass is the part that makes the archive useful. A folder of raw transcripts
is only marginally better than the chats themselves.

## `test_import_chat_export.py`

Tests for the importer. Standard library `unittest`, no pytest, no new
dependencies.

```bash
python3 aibos/tools/test_import_chat_export.py
```

They cover slug generation, both date formats, format detection, both
normalisers, the ChatGPT branch walk and its timestamp fallback, filtering,
rendering and filename collisions. CI runs them on every push.
