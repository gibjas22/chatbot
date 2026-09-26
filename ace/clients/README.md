# Client programmes

One folder per client programme, named exactly as `gibcom-ace-engine` Step 1
specifies:

```
[CLIENT] - [CATEGORY CODE] - ACE/
├── BRAND_VAULT.md          design authority
├── CONTENT_LEDGER.md       fact and memory authority
├── PRODUCTION_PROTOCOL.md  behaviour authority
├── campaigns/              one subfolder per campaign, created on demand
│   └── campaign-1/
│       └── asset-01-[slug].md
└── deliverables/           assembled packs
    └── campaign-1/
```

For example `Gibcom Marketing Support Ltd - DM05 - ACE/`.

## Starting one

Copy the three canon files from `../templates/`, then run the engine:

> Build ACE for [CLIENT] using [CODE]

`PRODUCTION_PROTOCOL.md` is copied unchanged, every time. It is the only canon
file that does not vary by client. The other two are written by the engine at
Steps 2 and 3.

## The shape of a finished programme

| | Count |
|---|---|
| Campaigns | 9 |
| Assets per campaign | 13 |
| Assets total | 117 |
| Deliverable packs | 9 |

Track progress with:

```bash
python3 ace/tools/ace_status.py --clients
```

## Two rules worth repeating

**Never skip `lock`.** It updates the ledger with everything from the completed
campaign. The ledger is what keeps Campaign 5 consistent with Campaign 2, and
skipping it once quietly breaks continuity for everything after.

**Never write prose before a plan is approved.** The plan is where errors are
cheap. Thirteen assets written against a wrong plan is a wasted campaign.

## Client confidentiality

Think before committing a client folder to a shared repository. Brand vaults and
content ledgers hold pricing, pipeline state, unpublished offers and named
customer stories with consent records. If this repository is or may become
public, keep client folders out of it: add them to `.gitignore` and hold them in
private storage instead. The templates and the library are safe to share; the
filled-in client folders usually are not.
