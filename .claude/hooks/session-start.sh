#!/bin/bash
#
# SessionStart hook for Claude Code on the web.
#
# Installs what the repository's own checks need, so a remote session can run
# the tests and the linter immediately rather than discovering halfway through
# a task that neither is available. Runs synchronously: the session starts a
# little later, but nothing races against a half-finished install.
#
# Local sessions are left alone; developers manage their own environments.

set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

echo "Installing runtime dependencies from requirements.txt"
python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt

# ruff is a development tool, kept out of requirements.txt so the application's
# runtime dependencies stay minimal. CI installs it the same way.
echo "Installing ruff"
python3 -m pip install --quiet --disable-pip-version-check ruff

# The test suite imports chat_errors and tools/ from the repository root.
echo 'export PYTHONPATH="."' >> "${CLAUDE_ENV_FILE:-/dev/null}"

echo "Session dependencies ready"
