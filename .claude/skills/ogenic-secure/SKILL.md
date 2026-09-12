---
name: ogenic-secure
description: "Secrets, input and dependency hygiene for the Ogenic toolkit. Use whenever the work touches API keys, tokens, passwords, .env files, credentials, user input reaching a shell, query, path or renderer, third-party dependencies, or when Gibson asks whether something is safe to commit or deploy. Also the security pass inside ogenic-review."
---

# Ogenic Secure

Most real incidents are dull: a key in a commit, an unvalidated path, an old dependency. Cover the dull ones properly.

## Secrets

### The rule

A secret never enters a tracked file. Not in code, config, tests, fixtures, notebooks, logs, screenshots or commit messages. Not "temporarily". Not with a comment saying to remove it later.

### Where they belong

| Context | Store it in |
|---|---|
| Local development | `.env`, git-ignored, loaded at runtime |
| Streamlit | `.streamlit/secrets.toml`, git-ignored, read via `st.secrets` |
| CI | The provider's encrypted secret store, injected as an environment variable |
| Production | The platform's secret manager, never baked into an image |

### Before every commit

```bash
git diff --staged | grep -nEi \
  'api[_-]?key|secret|password|passwd|token|bearer|authorization|private[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}'
```

The `strix` skill wraps this and more in a script that also covers private keys, JSON web
tokens, injection-prone code and credential files about to be tracked:

```bash
bash .claude/skills/strix/scripts/scan.sh
```

Any hit gets read by a human before the commit goes anywhere. Placeholders such as `your-api-key-here` are fine. Anything that looks real is treated as real.

### If a secret has been committed

Rotate first, clean second. The order matters, because the moment it hit a remote it must be assumed compromised, and history rewriting does not un-copy it.

1. Revoke and reissue the credential at the provider. Immediately.
2. Remove it from the working tree and commit that.
3. Purge it from history with `git filter-repo` or the provider's secret-removal tooling, then force-push with the team's agreement.
4. Check the logs for use of the key between exposure and revocation.
5. Add the pattern to a pre-commit scan so it cannot recur.

Never skip step 1 because "it was only pushed for a minute".

### Handling keys in application code

- Read from the environment or a secret store at the point of use, not at import time.
- Never log a key, never echo it back into the interface, never include it in an error message.
- Mask in any display: last four characters only.
- Treat a key entered by a user as belonging to that user. Never persist it server-side without saying so plainly.

## Input

Any value from outside the process is untrusted. That includes user input, API responses, file contents, environment variables and anything read from a database that a user once wrote to.

| Sink | Rule |
|---|---|
| Shell | Never build a command by string concatenation. Pass an argument list, never `shell=True` with interpolated input |
| SQL | Parameterised queries only. Never format a value into the statement |
| File path | Resolve, then confirm the result is inside the intended directory. Reject `..` and absolute paths |
| HTML, Markdown render | Escape by default. `unsafe_allow_html` and its equivalents need a written reason |
| Deserialisation | Never `pickle`, `eval`, `exec` or `yaml.load` on untrusted data. Use JSON or a safe loader |
| Redirect, fetch URL | Allowlist the host. Never fetch an arbitrary user-supplied URL from the server |

Validate at the boundary, once, then trust the validated value inwards. Validation scattered through the call stack is validation nobody can audit.

## Dependencies

- Add a dependency only when it earns its place. Twenty lines of the standard library beats a transitive tree you have not read.
- Pin versions in anything deployed. An unpinned dependency means the build is not reproducible and a supply-chain change lands without review.
- Check the basics before adding: is it maintained, how many maintainers, when was the last release, does the name look like a typosquat of something popular?
- Run the ecosystem's audit tool as part of CI, for instance `pip-audit` or `npm audit`, and treat a high finding as work.

## Data

- Log identifiers, never contents. A user id is fine, a message body is not.
- Redact personal data before it reaches an error tracker.
- Collect the minimum. Data you do not hold cannot leak.
- Anything you send to a third-party API leaves your control. Say so in the interface where a user would reasonably want to know.

## Pre-deploy checklist

- [ ] No secrets in the diff or in history for this branch.
- [ ] Every external input has a validation point.
- [ ] Every network call has a timeout and a handled failure.
- [ ] Errors shown to users say what to do, and leak no internals.
- [ ] Dependencies pinned, audit clean or findings triaged.
- [ ] `.gitignore` covers `.env`, `.streamlit/secrets.toml`, credential files and local databases.
- [ ] Debug modes, verbose logging and permissive CORS are off in production.

## What not to do

Do not build offensive tooling, credential-stuffing scripts, scrapers designed to evade blocks, or anything intended to gain access to a system without authorisation. Defensive work, hardening, authorised testing and incident response are in scope. Attacks are not.
