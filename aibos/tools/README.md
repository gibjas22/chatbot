# Tools

## `import_claude_export.py`

Turns a Claude data export into `../conversations/` files plus a regenerated
`../INDEX.md`. Standard library only, nothing leaves your machine.

### Getting the export

Claude does not let an agent session read your past conversations, so the
history has to come from an export you request yourself:

1. In Claude, open **Settings**, then **Privacy**, then **Export data**.
2. Claude emails you a download link. This usually takes a few minutes.
3. Download and unzip it. The file you need is `conversations.json`.

### Running it

```bash
# See what would be imported, without writing anything
python3 aibos/tools/import_claude_export.py ~/Downloads/claude-export/conversations.json --dry-run

# Do the import
python3 aibos/tools/import_claude_export.py ~/Downloads/claude-export/conversations.json

# Widen or narrow the filter
python3 aibos/tools/import_claude_export.py conversations.json --term aibos --term "voice layer"

# Import everything, no filtering
python3 aibos/tools/import_claude_export.py conversations.json --all

# Rebuild the index after editing frontmatter by hand
python3 aibos/tools/import_claude_export.py --index-only
```

By default it keeps conversations mentioning `aibos`, `command centre`,
`command center` or `gibcom` in the title or body, and skips everything else.
Run `--dry-run` first to check the filter is catching what you expect before
writing dozens of files.

### After importing

The importer cannot summarise for you, so each imported file has empty summary
sections above the transcript. Work through them and fill in what the session
was for, what was decided and what is still open. Set `topics` and `status` in
the frontmatter while you are there, then rerun with `--index-only`.

That pass is the part that makes the archive useful. A folder of raw transcripts
is only marginally better than the chats themselves.
