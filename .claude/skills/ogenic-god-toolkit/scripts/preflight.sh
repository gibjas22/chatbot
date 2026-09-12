#!/usr/bin/env bash
# Ogenic God Toolkit preflight.
# Detects what this project has and runs every available quality gate in one pass.
# Exit 0 = every gate that exists passed. Exit 1 = at least one failed.
#
# Usage: bash .claude/skills/ogenic-god-toolkit/scripts/preflight.sh

set -uo pipefail

PASS=0
FAIL=0
SKIP=0

have() { command -v "$1" >/dev/null 2>&1; }

gate() {
  local label="$1"; shift
  if ! have "$1"; then
    printf '  SKIP  %-28s (%s not installed)\n' "$label" "$1"
    SKIP=$((SKIP + 1))
    return 0
  fi
  local out
  if out=$("$@" 2>&1); then
    printf '  PASS  %s\n' "$label"
    PASS=$((PASS + 1))
  else
    printf '  FAIL  %s\n' "$label"
    printf '%s\n' "$out" | tail -25 | sed 's/^/        /'
    FAIL=$((FAIL + 1))
  fi
}

echo "Ogenic preflight"
echo "================"

# --- Python --------------------------------------------------------------
if ls ./*.py >/dev/null 2>&1 || [ -f pyproject.toml ] || [ -f requirements.txt ]; then
  echo
  echo "Python"
  gate "compile"      python3 -m compileall -q .
  [ -d tests ] || ls test_*.py >/dev/null 2>&1 && gate "pytest" pytest -q
  [ -f pyproject.toml ] || [ -f ruff.toml ] || [ -f .ruff.toml ] && gate "ruff lint" ruff check .
  [ -f mypy.ini ] || grep -q '\[tool.mypy\]' pyproject.toml 2>/dev/null && gate "mypy" mypy .
  [ -f requirements.txt ] && gate "pip-audit" pip-audit -r requirements.txt
fi

# --- Node ----------------------------------------------------------------
if [ -f package.json ]; then
  echo
  echo "Node"
  grep -q '"test"'  package.json && gate "npm test"  npm test --silent
  grep -q '"lint"'  package.json && gate "npm lint"  npm run lint --silent
  grep -q '"build"' package.json && gate "npm build" npm run build --silent
  [ -f tsconfig.json ] && gate "tsc" npx tsc --noEmit
fi

# --- Go ------------------------------------------------------------------
if [ -f go.mod ]; then
  echo
  echo "Go"
  gate "go vet"  go vet ./...
  gate "go test" go test ./...
fi

# --- Rust ----------------------------------------------------------------
if [ -f Cargo.toml ]; then
  echo
  echo "Rust"
  gate "cargo test"  cargo test --quiet
  gate "cargo clippy" cargo clippy --quiet -- -D warnings
fi

# --- Security ------------------------------------------------------------
echo
echo "Security"
if [ -f .claude/skills/strix/scripts/scan.sh ]; then
  if out=$(bash .claude/skills/strix/scripts/scan.sh --all 2>&1); then
    printf '  PASS  strix scan\n'
    PASS=$((PASS + 1))
  else
    printf '  FAIL  strix scan\n'
    printf '%s\n' "$out" | sed 's/^/        /'
    FAIL=$((FAIL + 1))
  fi
else
  printf '  SKIP  strix scan (not installed)\n'
  SKIP=$((SKIP + 1))
fi

# --- verdict -------------------------------------------------------------
echo
echo "================"
printf 'passed %d, failed %d, skipped %d\n' "$PASS" "$FAIL" "$SKIP"
if [ "$FAIL" -gt 0 ]; then
  echo "Not ready to ship. Fix the failures above."
  exit 1
fi
if [ "$PASS" -eq 0 ]; then
  echo "No gates ran. This project has no automated checks yet, so verify by hand and say so."
  exit 0
fi
echo "Ready to ship."
exit 0
