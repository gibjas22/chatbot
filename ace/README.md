# Gibcom ACE: Agentic Content Engine

The model folder structure for ACE, plus a coverage tracker. Owner: Gibson
Nyendwa, Gibcom Marketing Support Ltd.

## What ACE is

Three skills forming one pipeline, not three separate tools.

| Stage | Skill | Takes | Produces |
|---|---|---|---|
| Intake | `gibcom-ace-intake` | Call notes, a URL, documents | `[CLIENT]_Brand-Pack.md` plus `[ASK CLIENT]` questions |
| Library | `gibcom-ace-generator` | A category code and a lens | `library/[CODE]-[LENS]-[slug].md` |
| Production | `gibcom-ace-engine` | A brand pack and an engine brief | A client folder, 9 campaigns, 117 assets |

Intake and the library are both inputs to the engine. The engine is where the
work actually happens, and it will run without either, just less well.

## The numbers that shape it

| | |
|---|---|
| Categories | 48 (16 Digital Marketing, 16 AI Content, 16 Training) |
| Niche lenses | 7 |
| Engine briefs in the full matrix | **336** |
| Campaigns per programme | 9 |
| Assets per campaign | 13 |
| Assets per programme | **117** |

At the ten briefs a week the generator suggests, the matrix takes about 34
weeks. That scale is the whole reason this folder exists: 336 briefs and any
number of 117-asset programmes cannot be tracked in your head.

## Layout

| Path | Holds |
|---|---|
| `catalogue.json` | The fixed matrix as data. Drives the tracker |
| `CATALOGUE.md` | The same, readable |
| `library/` | The 336 engine briefs, plus `_TEMPLATE.md` |
| `clients/` | One folder per client programme |
| `templates/` | The three canon files the engine expects |
| `tools/ace_status.py` | Coverage and progress reporting |

## The content list

```bash
python3 ace/tools/ace_status.py              # coverage against 336
python3 ace/tools/ace_status.py --matrix     # the full 48 x 7 grid
python3 ace/tools/ace_status.py --missing --lens L2   # what to build next
python3 ace/tools/ace_status.py --clients    # programme progress
```

`--clients` reports canon files present, campaigns started, assets written
against 117, and packs assembled, per client.

## What holds it together

Reading the engine skill closely, three mechanisms do the real work. They are
worth understanding before using any of this.

**Canon priority.** `BRAND_VAULT.md` governs strategy and design.
`CONTENT_LEDGER.md` governs facts, prices, dates, claims, proof and publishing
history. When they conflict the engine stops and reconciles rather than
guessing. That rule is what stops a nine-campaign programme drifting.

**The ledger as memory.** `lock` writes each completed campaign into the ledger,
and nothing is ever deleted, only retired. This is what makes Campaign 5
consistent with Campaign 2. Skipping `lock` once breaks continuity for
everything after it, silently.

**The proof rule.** Only proof recorded in the ledger may be used. Anything
unproven is marked `[PROOF NEEDED]` and logged rather than written around. For a
business making claims under ASA/CAP rules and sector regulators, this is the
part that keeps the output publishable.

## Two observations from the analysis

**The seeds mechanism is the commercially interesting part.** Every programme
plants three named loose ends, and `bridge forward` harvests at least two into
the next quarter's programme. That turns a one-off nine-campaign deliverable
into a renewing engagement, and it is designed in rather than bolted on.

**Continuity is the product.** Anyone can generate 117 assets. What is hard, and
what the ledger and canon priority exist to protect, is 117 assets that do not
contradict each other on price, claim or story across nine campaigns. That is
the thing worth charging for.

## Related

`../aibos/` is the AIBOS Command Centre folder: conversations, decisions and
knowledge. Different project, same instinct, which is that context worth keeping
belongs in version control rather than in a chat window.
