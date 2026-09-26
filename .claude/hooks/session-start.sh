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

# requirements-dev.txt, not a bare `pip install ruff`. It pins the same ruff CI
# pins, and an unpinned install is actively harmful here: pip puts it in
# ~/.local/bin, which precedes /usr/local/bin on PATH, so a newer ruff silently
# shadows the pinned one and reports findings CI never will. That exact shadow
# was observed in this repository, 0.15.8 masking the pinned 0.16.7.
echo "Installing the pinned development toolchain from requirements-dev.txt"
python3 -m pip install --quiet --disable-pip-version-check -r requirements-dev.txt

# The test suite imports chat_core and tools/ from the repository root.
echo 'export PYTHONPATH="."' >> "${CLAUDE_ENV_FILE:-/dev/null}"

echo "Session dependencies ready"
