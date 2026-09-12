# Conversations

One file per captured chat. Filenames are `YYYY-MM-DD-short-slug.md` so the
folder sorts chronologically.

Two ways to add one:

- **By hand:** copy `_TEMPLATE.md`, fill it in, rename it, commit it.
- **By import:** run the importer in `../tools/`, which writes files here
  automatically from a Claude data export.

Every file carries YAML frontmatter. The `topics` and `status` fields are what
make the folder searchable later, so fill them in properly rather than leaving
the placeholders.

Keep summaries at the top and raw transcript at the bottom. When you or Claude
read one of these files months from now, the first thirty lines should be enough
to reload the context.
