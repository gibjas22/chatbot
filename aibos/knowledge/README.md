# Knowledge

Stable reference material for AIBOS. Unlike `../conversations/`, which is a
record of what happened, this folder describes what is true right now.

Suggested files, added as the project needs them:

| File | Holds |
|---|---|
| `architecture.md` | How the Command Centre fits together, and the boundaries between parts |
| `providers.md` | Which external services are used, for what, and where their credentials live. Names and purposes only, never the credentials themselves |
| `conventions.md` | Naming, structure and style rules the project follows |
| `glossary.md` | Project specific terms, so they mean the same thing in every session |

Keep these short and current. A file here that has gone stale is worse than no
file at all, because it will be trusted.

Never commit an API key, token or secret to this folder or anywhere else in the
repository. The `gibcom-aibos-keys` skill covers where they should live instead.
