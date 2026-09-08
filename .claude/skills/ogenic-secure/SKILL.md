---
name: ogenic-secure
description: "Secret, input and dependency hygiene specific to this repository. Use whenever the work touches API keys, tokens, .env files, credentials, user input reaching a shell, query, path or renderer, or third-party dependencies, and when Gibson asks whether something is safe to commit or deploy. Carries the recovery procedure for a committed credential and this repository's own rules; run the /security-review command for a diff-level pass."
---

# Ogenic Secure

Most real incidents are dull: a key in a commit, an unvalidated path, an old
dependency. This covers the dull ones and the rules particular to here.

For a security pass over a branch diff, run the `/security-review` command. This
skill is the standing rules and the recovery procedure, not a review pass.

## This repository's own rules

The application takes an API key from the user and sends their messages to a
third party, so these are not theoretical.

- **Never surface a raw OpenAI error.** OpenAI puts the offending key into the
  message text of an authentication error. Everything shown to a user goes
  through `chat_errors.safe_error_text`. If you add another error path, route it
  through there too, and add a test.
- **The user's key belongs to the user.** Never persist it, never log it, never
  put it in an error message or a URL. It stays in the session.
- **`.gitignore` already covers** `.env` and `.streamlit/secrets.toml`. Keep it
  that way.
- **CI scans every tracked file** for credential patterns. The validator, the
  workflow, `.claude` and the two test files that assert the scanners fire are
  excluded by name, because they carry the patterns on purpose. Never widen that
  to skip `tests/` wholesale: a credential in a future test file must still be
  caught.

## Secrets

### The rule

A secret never enters a tracked file. Not in code, config, tests, fixtures,
notebooks, logs, screenshots or commit messages. Not "temporarily", and not with
a comment saying to remove it later.

### Before every commit

```bash
git diff --staged | grep -nEi \
  'api[_-]?key|secret|password|token|bearer|private[_-]?key|sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}'
```

Placeholders such as `your-api-key-here` are fine. Anything that looks real is
treated as real.

### If a secret has been committed

Rotate first, clean second. The order matters: the moment it reached a remote it
must be assumed compromised, and rewriting history does not un-copy it.

1. **Revoke and reissue at the provider. Immediately.**
2. Remove it from the working tree and commit that.
3. Purge it from history with `git filter-repo` or the provider's tooling, then
   force-push with the team's agreement.
4. Check the provider's logs for use between exposure and revocation.
5. Add the pattern to the CI scan so it cannot recur.

Never skip step 1 because "it was only pushed for a minute".

## Input

Any value from outside the process is untrusted: user input, API responses, file
contents, environment variables, and anything read from a store a user once
wrote to.

| Sink | Rule |
|---|---|
| Shell | Pass an argument list. Never `shell=True` with interpolated input |
| SQL | Parameterised queries only |
| File path | Resolve, then confirm it is inside the intended directory |
| HTML render | Escape by default. `unsafe_allow_html` needs a written reason |
| Deserialisation | Never `pickle`, `eval`, `exec` or `yaml.load` on untrusted data |
| Fetched URL | Allowlist the host |

Validate at the boundary, once, then trust the validated value inwards.

## Dependencies

- Pinned to a major version on purpose. `openai` has reached 3.x while this code
  targets the 1.x interface, so moving majors is a deliberate, tested migration.
- Dependabot watches pip and the GitHub Actions weekly.
- Add a dependency only when it earns its place. Twenty lines of the standard
  library beats a transitive tree you have not read.
- Before adding one: maintained, how many maintainers, last release, and does the
  name look like a typosquat?

## Pre-deploy checklist

- [ ] No secrets in the diff or in this branch's history.
- [ ] Every external input has a validation point.
- [ ] Every network call has a timeout and a handled failure.
- [ ] Errors shown to users say what to do, and leak no internals or credentials.
- [ ] Dependencies pinned, Dependabot findings triaged.
- [ ] Debug modes and verbose logging off in production.

## Out of bounds

No offensive tooling, credential-stuffing, block-evading scrapers, or anything
intended to reach a system without authorisation. Hardening, authorised testing
and incident response are in scope. Attacks are not.
