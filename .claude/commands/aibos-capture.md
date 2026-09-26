---
description: Capture this session into the AIBOS project folder as a conversation file
argument-hint: [optional short title for the session]
---

Capture the current session into `aibos/conversations/` so the context survives
into the next one.

$ARGUMENTS

Work through this in order.

## 1. Decide whether there is anything worth capturing

A session is worth a file if it decided something, built something, or surfaced
an open question that the next session would otherwise rediscover. A session
that only answered a lookup question is not. If there is nothing worth keeping,
say so plainly and stop rather than writing an empty file.

## 2. Gather the facts before writing

- What we were trying to do, stated as a goal rather than a transcript.
- What was decided, and the reason behind each decision.
- What was actually built or changed: files, services, configuration, commits,
  pull requests. Use real paths and real numbers, not approximations.
- What is still open.

Do not invent any of this. If something was discussed but never settled, it
belongs under open threads, not under decisions.

## 3. Write the file

Copy the structure of `aibos/conversations/_TEMPLATE.md`. Save as
`aibos/conversations/YYYY-MM-DD-short-slug.md` using today's date and a slug of
three to five words.

Fill in the frontmatter properly:

- `title` — what the session was about, not a restatement of the date
- `date` — today, ISO format
- `source` — `claude-code` for this session
- `topics` — a real list, drawn from what the session touched. Reuse topic names
  already present in other conversation files rather than inventing near
  duplicates. Check `aibos/INDEX.md` first.
- `status` — `settled` if the work concluded, `active` if it continues,
  `abandoned` if it was dropped

Keep the summary sections tight. Someone reading the first thirty lines months
from now should be able to reload the context without reading further. Put
anything worth keeping verbatim under a `## Raw notes` heading at the bottom,
and trim the rest.

## 4. Promote anything that qualifies as a decision

If the session settled something whose reversal would cost real work, choice of
provider, data model, authentication approach, deployment target, naming
convention, also write it to `aibos/decisions/` as `NNNN-short-slug.md`, using
the next free sequence number. Follow the four part structure in
`aibos/decisions/README.md`: context, decision, reasoning, consequences.

Day to day implementation choices stay in the conversation file. Do not inflate
the decisions folder.

## 5. Update the knowledge folder if the session changed what is true

If the session confirmed or changed something described in `aibos/knowledge/`,
update it. `architecture.md` in particular carries `[CONFIRM]` and `[TO FILL]`
markers; replace any the session has now answered.

## 6. Regenerate the index

```bash
python3 aibos/tools/import_chat_export.py --index-only
```

## 7. Report back

Tell Gibson the path of the file written, the topics set, whether a decision
record was created, and anything you deliberately left out. Do not commit unless
he asks; `/ship` handles that.

Never write a credential, token or key into any of these files.
