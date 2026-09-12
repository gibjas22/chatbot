# Where each credential belongs

| Credential | Local development | CI | Production |
| --- | --- | --- | --- |
| LLM API key | `.env` or `.streamlit/secrets.toml`, gitignored | Platform secret store | Platform secret store or a managed vault |
| Database URL | `.env` | Platform secret | Injected by the host |
| OAuth client secret | `.env` | Platform secret | Vault, rotated on schedule |
| Signing key | Generated locally, never committed | Platform secret | Vault, rotated on schedule |
| Public client ID | May be committed | Committed | Committed |

## Rules

1. A secret that has touched a git commit is burnt. Rotate it, do not just delete the line.
   `git rm --cached` does not remove it from history.
2. Every project ships a `.env.example` with the variable names and placeholder values, so the
   real names are documented without leaking anything.
3. Read secrets once at startup into module level constants. Do not pass them through function
   arguments where they can end up in a traceback.
4. Never print, log or include a secret in an error message. Log the variable name only.
5. When asking Gibson for a key, tell him where to put it. Never ask him to paste it into chat.
6. In a shared or public deployment, a key the visitor supplies belongs only to that session.
   Never write it to disk, a database or a log.

## Checking history for a leak

```bash
git log -p --all -S 'sk-' -- . | head -50
git log -p --all -S 'BEGIN PRIVATE KEY' -- . | head -50
git log --all --name-only --pretty=format: | sort -u | grep -Ei '\.env|secret|credential|\.pem$'
```

If anything turns up, rotate first, then clean history with `git filter-repo` and force push
after telling Gibson what will happen to anyone else's clone.
