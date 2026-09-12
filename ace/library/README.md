# Engine Brief library

The 336 engine briefs: 48 categories x 7 niche lenses.

Each brief is what `gibcom-ace-engine` reads alongside its own rules when
building a programme. It carries the category-specific and niche-specific
material the engine cannot know on its own.

## Naming

```
[CODE]-[LENS]-[slug].md
```

For example `DM01-L2-local-service-authority.md`. This pattern is not
decoration: `../tools/ace_status.py` parses it to report coverage, so a brief
named any other way is invisible to the tracker. Codes come from
`../catalogue.json` and are fixed; the generator skill states category names
must not be renamed.

## Building them

Copy `_TEMPLATE.md`, or ask the generator skill:

> Generate an engine brief for DM01, lens L2.

Batch ten at a time with "build the library" or "batch ten". Ten a week fills
the matrix in about eight months, which `ace_status.py` will confirm as you go.

## Where to start

Not at DM01-L1 and onward alphabetically. Two better orders:

1. **Lens first.** Pick the lens you sell into most and build its 48 categories.
   That gives you a complete offer for one market rather than a thin spread
   across seven.
2. **Pilot Season.** The generator's own rule: three Campaign 1s, greenlight the
   winner. Build the three briefs you would pitch this month.

Check coverage any time with:

```bash
python3 ace/tools/ace_status.py --matrix
python3 ace/tools/ace_status.py --missing --lens L2
```
