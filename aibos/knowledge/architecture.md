# AIBOS architecture

How the Gibcom AIBOS Command Centre fits together, and the boundaries between
its parts.

> **Status: starter.** The sections below are scaffolded from what the
> `gibcom-aibos-keys` and `gibcom-aibos-leadgen` skill definitions already
> describe. Anything marked **[CONFIRM]** is inferred from those descriptions
> rather than from the running system, so check it before relying on it.
> Anything marked **[TO FILL]** was not derivable and needs your input.

## What AIBOS is

A governed AI business operating system for Gibcom Marketing Support Ltd. It
runs recurring business operations under an agent layer rather than by hand, so
work that would otherwise depend on Gibson being at a keyboard happens on a
schedule and reports back.

## Components

| Component | Responsibility | Status |
|---|---|---|
| Voice layer | Speech in and out for briefings and interaction | **[CONFIRM]** exists per the keys skill; providers and routing **[TO FILL]** |
| Agents | The units that carry out work against a defined process | **[CONFIRM]** referenced; inventory **[TO FILL]** |
| Processes | Governed, repeatable procedures the agents follow | **[CONFIRM]** referenced; list **[TO FILL]** |
| Morning briefing | Scheduled daily digest, including the lead section | **[CONFIRM]** referenced by both skills; schedule and delivery channel **[TO FILL]** |
| Leadgen module | Mines the UK Companies House register for prospects. Lives in `leadgen/companies_house` | **[CONFIRM]** per the leadgen skill |
| MCP servers | How AIBOS reaches external tools and data | **[CONFIRM]** referenced; which servers are wired **[TO FILL]** |

## The leadgen module

The best specified part. It watches the UK Companies House register for signals
that a business may need Gibcom's services:

- new incorporations
- rebrands
- relocations
- new directors
- share allotments

Filtered by SIC code, surfaced as a daily lead report, and fed into the morning
briefing's lead section.

Companies House exposes several APIs: public data, streaming, document, identity
and filing, plus a sandbox. **[TO FILL]** which of these AIBOS actually uses.

## External providers

Named in the `gibcom-aibos-keys` skill as providers AIBOS holds credentials for.
Presence here means a credential path exists, not that the provider is currently
in active use. **[CONFIRM]** which are live.

| Provider | Likely role |
|---|---|
| Groq | Fast inference **[CONFIRM]** |
| ElevenLabs | Speech synthesis for the voice layer **[CONFIRM]** |
| Grok (xAI) | Model provider **[CONFIRM]** |
| Anthropic | Model provider **[CONFIRM]** |
| OpenAI | Model provider **[CONFIRM]** |
| Google (Gemini, Cloud, Workspace) | Models plus workspace data **[CONFIRM]** |
| Ollama | Local inference **[CONFIRM]** |
| Companies House | Leadgen source, confirmed by the leadgen skill |
| GitHub | Code and automation **[CONFIRM]** |
| Devin, Composio, Zapier, Notion, Base44, Autocalls | Integration and automation surface **[CONFIRM]** |

Credentials themselves never appear in this repository. The
`gibcom-aibos-keys` skill governs where they live and how they are rotated.

## Data flow

**[TO FILL]** The path a piece of work takes from trigger to output. Worth
drawing once as a simple list: what fires, what it reads, what it writes, who
sees the result.

## Boundaries and rules

**[TO FILL]** What AIBOS is allowed to do without asking, and what always needs
Gibson's approval. This is the "governed" half of the name and is the section
most worth writing properly, because it is the one that matters when an agent
does something unexpected.

## Open questions

- Where does AIBOS actually run: local machine, server, scheduled cloud jobs?
- What is the failure behaviour when a provider is down or a key has expired?
- What is the single source of truth for the lead list once leads are generated?

## How to maintain this file

Replace the markers as you confirm each part. A file here that has gone stale is
worse than no file, because it will be trusted. When something significant
changes, record why in `../decisions/` and update the affected rows here.
