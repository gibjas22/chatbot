#!/usr/bin/env bash
# Strix pre-commit scanner.
# Scans the staged diff for credentials, private keys, risky files and debug leftovers.
# Exit 0 = clean. Exit 1 = findings. Exit 2 = usage error.
#
# Usage:
#   bash .claude/skills/strix/scripts/scan.sh           # staged changes (default)
#   bash .claude/skills/strix/scripts/scan.sh --all     # whole working tree
#   bash .claude/skills/strix/scripts/scan.sh --range main..HEAD

set -uo pipefail

MODE="staged"
RANGE=""

while [ $# -gt 0 ]; do
  case "$1" in
    --all) MODE="all"; shift ;;
    --range) MODE="range"; RANGE="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "strix: not a git repository" >&2
  exit 2
fi

# Prose is excluded from the code-smell checks. Documenting a dangerous pattern is
# not committing one, and a security skill that flags its own examples is noise.
# Credential checks still run over every file: a real key in a markdown file leaks
# exactly as badly as one in source.
# The scanner defines these patterns as literals, so it matches itself. Excluded for
# the same reason the repository's CI excludes its own validator.
PROSE=(':!*.md' ':!*.rst' ':!*.txt' ':!docs/**' ':!.claude/skills/strix/scripts/scan.sh')

case "$MODE" in
  staged) DIFF=$(git diff --cached -U0)
          CODE_DIFF=$(git diff --cached -U0 -- . "${PROSE[@]}")
          FILES=$(git diff --cached --name-only --diff-filter=ACM) ;;
  all)    DIFF=$(git diff HEAD -U0)
          CODE_DIFF=$(git diff HEAD -U0 -- . "${PROSE[@]}")
          FILES=$(git ls-files) ;;
  range)  [ -n "$RANGE" ] || { echo "strix: --range needs a value" >&2; exit 2; }
          DIFF=$(git diff "$RANGE" -U0)
          CODE_DIFF=$(git diff "$RANGE" -U0 -- . "${PROSE[@]}")
          FILES=$(git diff "$RANGE" --name-only --diff-filter=ACM) ;;
esac

# `git diff HEAD` is empty on a clean tree, so --all falls back to scanning tracked
# content itself rather than silently reporting a clean scan of nothing.
if [ "$MODE" = "all" ] && [ -z "$DIFF" ]; then
  DIFF=$(git grep -nI '' -- . 2>/dev/null | sed 's/^/+/')
  CODE_DIFF=$(git grep -nI '' -- . "${PROSE[@]}" 2>/dev/null | sed 's/^/+/')
fi

FINDINGS=0

report() {
  FINDINGS=$((FINDINGS + 1))
  printf '\n[%s] %s\n' "$1" "$2"
  [ -n "${3:-}" ] && printf '%s\n' "$3" | sed 's/^/    /'
  return 0
}

# Only look at added lines.
ADDED=$(printf '%s\n' "$DIFF" | grep -E '^\+' | grep -Ev '^\+\+\+' || true)
ADDED_CODE=$(printf '%s\n' "$CODE_DIFF" | grep -E '^\+' | grep -Ev '^\+\+\+' || true)

# check - runs over every added line, prose included. For leaked data.
check() {
  local sev="$1" label="$2" pattern="$3"
  local hits
  hits=$(printf '%s\n' "$ADDED" | grep -Ein "$pattern" | head -5 || true)
  [ -n "$hits" ] && report "$sev" "$label" "$hits"
}

# check_code - skips prose. For patterns that describe dangerous code, which a
# document may legitimately mention.
check_code() {
  local sev="$1" label="$2" pattern="$3"
  local hits
  hits=$(printf '%s\n' "$ADDED_CODE" | grep -Ein "$pattern" | head -5 || true)
  [ -n "$hits" ] && report "$sev" "$label" "$hits"
}

# --- credential patterns -------------------------------------------------
check CRITICAL "OpenAI-style API key"        'sk-[A-Za-z0-9_-]{20,}'
check CRITICAL "Anthropic API key"           'sk-ant-[A-Za-z0-9_-]{20,}'
check CRITICAL "AWS access key id"           'AKIA[0-9A-Z]{16}'
check CRITICAL "Google API key"              'AIza[0-9A-Za-z_-]{35}'
check CRITICAL "GitHub token"                'gh[pousr]_[A-Za-z0-9]{30,}'
check CRITICAL "Slack token"                 'xox[baprs]-[A-Za-z0-9-]{10,}'
check CRITICAL "Stripe secret key"           'sk_live_[A-Za-z0-9]{20,}'
check CRITICAL "Private key block"           'BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY'
check CRITICAL "JSON web token literal"      'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}'
check HIGH     "Assigned secret literal"     '(password|passwd|secret|api_key|apikey|token|access_key)[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"']{8,}'
check HIGH     "Database URL with password"  '(postgres|postgresql|mysql|mongodb(\+srv)?|redis)://[^:@/[:space:]]+:[^@/[:space:]]+@'

# --- risky code patterns -------------------------------------------------
check_code HIGH   "shell=True with interpolation" 'subprocess\.[a-z_]+\(.*(f["'"'"']|%|\+|\.format\().*shell[[:space:]]*=[[:space:]]*True'
check_code HIGH   "eval or exec on a variable"    '\b(eval|exec)\([a-zA-Z_]'
check_code HIGH   "pickle load"                   'pickle\.loads?\('
yaml_hits=$(printf '%s\n' "$ADDED_CODE" | grep -Ein 'yaml\.load\(' | grep -Eiv 'SafeLoader|safe_load' | head -5 || true)
[ -n "$yaml_hits" ] && report HIGH "yaml.load without SafeLoader" "$yaml_hits"
check_code HIGH   "TLS verification disabled"     '(verify[[:space:]]*=[[:space:]]*False|CURLOPT_SSL_VERIFYPEER.*0|rejectUnauthorized[[:space:]]*:[[:space:]]*false)'
check_code MEDIUM "SQL built by interpolation"    '(execute|query)\([[:space:]]*(f["'"'"']|["'"'"'].*["'"'"'][[:space:]]*[%+])'
check_code MEDIUM "Raw HTML rendering enabled"    'unsafe_allow_html[[:space:]]*=[[:space:]]*True|dangerouslySetInnerHTML'
check_code MEDIUM "Wildcard CORS"                 'origins[[:space:]]*=[[:space:]]*["'"'"']\*|Access-Control-Allow-Origin.*\*'
check_code LOW    "Debug mode on"                 'debug[[:space:]]*=[[:space:]]*True|DEBUG[[:space:]]*=[[:space:]]*[Tt]rue'
check_code LOW    "Leftover debug statement"      '\b(pdb\.set_trace|breakpoint\(\)|console\.log|debugger)\b'

# --- risky files ---------------------------------------------------------
if [ -n "$FILES" ]; then
  RISKY=$(printf '%s\n' "$FILES" | grep -Ei '(^|/)\.env($|\.)|secrets\.toml$|\.pem$|\.key$|\.p12$|\.pfx$|credentials\.json$|service-account.*\.json$' || true)
  [ -n "$RISKY" ] && report CRITICAL "Credential file about to be tracked" "$RISKY"

  BIG=""
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    sz=$(wc -c <"$f" 2>/dev/null || echo 0)
    [ "$sz" -gt 5242880 ] && BIG="$BIG$f ($((sz/1048576)) MB)\n"
  done <<< "$FILES"
  [ -n "$BIG" ] && report LOW "Large file in commit" "$(printf '%b' "$BIG")"
fi

# --- gitignore hygiene ---------------------------------------------------
if [ -f .gitignore ]; then
  for p in ".env" "*.pem" "*.key"; do
    grep -qF -- "$p" .gitignore || report LOW "gitignore missing pattern" "$p"
  done
else
  report MEDIUM "No .gitignore in repository" ""
fi

# --- verdict -------------------------------------------------------------
echo
if [ "$FINDINGS" -eq 0 ]; then
  echo "strix: clean, $FINDINGS findings"
  exit 0
fi
echo "strix: $FINDINGS finding(s). Review each before committing."
echo "A false positive is fine to wave through. A real key is not: rotate it, do not just delete the line."
exit 1
