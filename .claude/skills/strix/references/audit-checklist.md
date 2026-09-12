# Strix deep audit checklist

Work top to bottom. Skip a section only when it genuinely does not apply, and say which sections
were skipped in the report.

## 1. Secrets and credentials

- [ ] No literal key, token, password or connection string in any tracked file.
- [ ] No secret in git history. Check with `git log -p --all -S'sk-'` and similar patterns.
- [ ] `.gitignore` covers `.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`, `secrets.toml`,
      `credentials.json`, `service-account*.json`.
- [ ] `.env.example` exists with placeholder values, so nobody invents their own names.
- [ ] Secrets are read once at startup, not passed around or logged.
- [ ] Any key that has ever been committed is treated as burnt and rotated.

## 2. Input handling

- [ ] Every external input is validated for type, length and range before use.
- [ ] SQL uses parameterised queries. No f-strings or concatenation into a query.
- [ ] Shell calls avoid `shell=True`. Arguments are passed as a list.
- [ ] File paths from users are resolved and confirmed to sit inside the intended directory.
      `../` traversal is rejected.
- [ ] File uploads are capped in size, checked by content type, and stored outside the web root
      with a generated filename.
- [ ] Deserialisation never uses `pickle`, `yaml.load` or `eval` on untrusted data.

## 3. Output handling

- [ ] User or model text is escaped before rendering as HTML.
- [ ] `unsafe_allow_html` and equivalents are off unless the content is authored by us.
- [ ] Error pages and API responses do not leak stack traces, file paths or query text.
- [ ] Logs do not contain credentials, tokens, full card numbers or personal data.

## 4. Authentication and authorisation

- [ ] Passwords hashed with bcrypt, scrypt or argon2. Never MD5, SHA1 or plain SHA256.
- [ ] Sessions use signed, httpOnly, secure cookies with a sane expiry.
- [ ] Every protected endpoint checks authorisation server side, not just in the UI.
- [ ] Object access is checked against the requesting user. No trusting an ID from the client.
- [ ] Rate limiting on login, password reset and any expensive endpoint.

## 5. Dependencies and supply chain

- [ ] Every dependency name is spelled correctly and is the package actually intended.
- [ ] Versions are pinned for anything deployed.
- [ ] Run `pip-audit` or `npm audit` and record the result.
- [ ] No install script from an unverified source is piped into a shell.
- [ ] Lockfile changes in a diff are reviewed, not waved through.

## 6. Network and transport

- [ ] HTTPS everywhere. No certificate verification disabled.
- [ ] CORS lists specific origins. Never `*` alongside credentials.
- [ ] No internal hostname, private IP or infrastructure detail in client-facing code.
- [ ] Timeouts set on every outbound request.

## 7. LLM specific

- [ ] Untrusted text is delimited and labelled as data in the prompt.
- [ ] Model output never reaches a shell, a database write, a file delete or a payment call
      without an explicit check.
- [ ] Token and conversation length are capped, so cost cannot run away.
- [ ] System prompt contains no secret, since a determined user can often extract it.
- [ ] Tool permissions given to an agent are the narrowest set that does the job.

## 8. Repository and CI

- [ ] No secret in workflow files. CI uses the platform's secret store.
- [ ] Workflows triggered by outside contributors cannot read secrets.
- [ ] Branch protection on the default branch.
- [ ] `CODEOWNERS` reflects who should actually review.

## Report format

For each finding:

**Severity** (critical, high, medium, low) — file and line — one sentence on the defect.
Then the concrete failure scenario: what an attacker does, and what they get.
Then the fix, as a diff or exact instruction.

No finding without a failure scenario. If you cannot describe how it fails in practice, it is
an observation, not a finding, and belongs in a short notes section at the end.
