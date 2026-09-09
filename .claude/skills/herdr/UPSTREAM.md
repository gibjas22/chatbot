# Provenance of `SKILL.md`

`SKILL.md` in this directory is **not written here**. It is a verbatim copy of
the agent skill that the Herdr project ships with its binary.

| | |
|---|---|
| Upstream | https://github.com/herdrdev/herdr |
| Path upstream | `skills/herdr/SKILL.md` |
| Pinned commit | `b9ce96869e89937278d673d70ae4c135dd318469` (2026-09-09) |
| Herdr version at that commit | 0.9.0 |
| Licence | Apache-2.0, see https://github.com/herdrdev/herdr/blob/master/LICENSE |
| SHA-256 of the vendored file | `25a68bc36d9309048db89e7d168f2e04d1689d734c5d72cc3688bf4ff9db1e9f` |

## Do not edit `SKILL.md`

Edit it and the next refresh silently reverts your change, or worse, a merge
conflict makes someone reconcile a file they did not write. If something in it
is wrong, raise it upstream.

## Refreshing it

The binary bundles the skill at build time, so the copy that matches an
installed Herdr is the one the binary prints:

```bash
herdr --skill > .claude/skills/herdr/SKILL.md
```

Without Herdr installed, take it from the source of truth and re-pin the table
above:

```bash
curl -fsSL https://raw.githubusercontent.com/herdrdev/herdr/master/skills/herdr/SKILL.md \
  -o .claude/skills/herdr/SKILL.md
sha256sum .claude/skills/herdr/SKILL.md
```

Then run `python3 tools/ogenic/validate_toolkit.py` before committing, because
a skill whose frontmatter breaks does not load and says nothing about it.

## Why it is vendored rather than installed

Herdr's own documented route is `npx skills add herdrdev/herdr --skill herdr -g`,
which writes into the user's global skills directory. That is the right command
on Gibson's own machine and it is what `docs/OGENIC_GOD_MODE.md` recommends
there.

It does not survive here. Remote Claude Code sessions get a fresh container that
is reclaimed when the session ends, so a globally installed skill is gone by the
next session. A file committed to this repository is present in every session,
on every machine, with no install step. That is the whole reason it lives here.

## It is inert without Herdr

The skill's first instruction is to check `HERDR_ENV=1` and stop if it is unset.
Outside a Herdr pane it does nothing, so carrying it costs a file and no
behaviour.
