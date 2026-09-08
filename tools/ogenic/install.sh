#!/usr/bin/env bash
#
# Install the Ogenic God Mode toolkit into a project or into your user config.
#
#   ./tools/ogenic/install.sh                    # into ./.claude of the current directory
#   ./tools/ogenic/install.sh --user             # into ~/.claude, available in every project
#   ./tools/ogenic/install.sh --target ../other  # into another project
#   ./tools/ogenic/install.sh --dry-run          # show what would happen, change nothing
#   ./tools/ogenic/install.sh --uninstall        # remove the Ogenic skills and commands
#
# Existing files are never overwritten unless --force is given.

set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_CLAUDE="${SOURCE_ROOT}/.claude"

TARGET_BASE="$(pwd)"
DRY_RUN=0
FORCE=0
UNINSTALL=0

SKILLS=(
  ogenic-god-mode
  ogenic-code-workflow
  ogenic-scaffold
  ogenic-debug
  ogenic-review
  ogenic-secure
  ogenic-ship
)

COMMANDS=(
  god-mode.md
  build.md
  debug.md
  review.md
  secure.md
  ship.md
)

usage() {
  # Print the comment block at the top of this file, stopping at the first
  # line that is not a comment.
  awk 'NR == 1 { next } /^#/ { sub(/^# ?/, ""); print; next } { exit }' "${BASH_SOURCE[0]}"
  exit 0
}

log()  { printf '%s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

run() {
  if [[ $DRY_RUN -eq 0 ]]; then
    "$@"
  fi
}

# "installed" when we really did, "would install" during a dry run.
did() {
  if [[ $DRY_RUN -eq 1 ]]; then
    printf '  would %s\n' "$*"
  else
    printf '  %sed %s\n' "${1%e}" "${*:2}"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)      TARGET_BASE="${HOME}"; shift ;;
    --target)    TARGET_BASE="${2:?--target needs a path}"; shift 2 ;;
    --dry-run)   DRY_RUN=1; shift ;;
    --force)     FORCE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help)   usage ;;
    *)           die "unknown option: $1 (try --help)" ;;
  esac
done

[[ -d "$SOURCE_CLAUDE" ]] || die "cannot find the toolkit source at ${SOURCE_CLAUDE}"
[[ -d "$TARGET_BASE" ]]   || die "target directory does not exist: ${TARGET_BASE}"

TARGET_CLAUDE="${TARGET_BASE%/}/.claude"

if [[ "$SOURCE_CLAUDE" == "$TARGET_CLAUDE" ]]; then
  die "source and target are the same directory; nothing to do"
fi

if [[ $UNINSTALL -eq 1 ]]; then
  log "Removing the Ogenic God Mode toolkit from ${TARGET_CLAUDE}"
  removed=0
  for skill in "${SKILLS[@]}"; do
    if [[ -d "${TARGET_CLAUDE}/skills/${skill}" ]]; then
      run rm -rf "${TARGET_CLAUDE}/skills/${skill}"
      did remove "skill   ${skill}"
      removed=$((removed + 1))
    fi
  done
  for command in "${COMMANDS[@]}"; do
    if [[ -f "${TARGET_CLAUDE}/commands/${command}" ]]; then
      run rm -f "${TARGET_CLAUDE}/commands/${command}"
      did remove "command ${command}"
      removed=$((removed + 1))
    fi
  done
  log ""
  if [[ $DRY_RUN -eq 1 ]]; then
    log "Would remove ${removed} item(s)."
  else
    log "Removed ${removed} item(s). Your own skills and commands were left alone."
  fi
  exit 0
fi

log "Installing the Ogenic God Mode toolkit"
log "  from: ${SOURCE_CLAUDE}"
log "  into: ${TARGET_CLAUDE}"
[[ $DRY_RUN -eq 1 ]] && log "  mode: dry run, nothing will be written"
log ""

run mkdir -p "${TARGET_CLAUDE}/skills" "${TARGET_CLAUDE}/commands"

installed=0
skipped=0

for skill in "${SKILLS[@]}"; do
  src="${SOURCE_CLAUDE}/skills/${skill}"
  dest="${TARGET_CLAUDE}/skills/${skill}"

  if [[ ! -d "$src" ]]; then
    warn "source skill missing, skipping: ${skill}"
    continue
  fi

  if [[ -e "$dest" && $FORCE -eq 0 ]]; then
    log "  skipped skill   ${skill} (already present, use --force to replace)"
    skipped=$((skipped + 1))
    continue
  fi

  run rm -rf "$dest"
  run cp -R "$src" "$dest"
  did install "skill   ${skill}"
  installed=$((installed + 1))
done

for command in "${COMMANDS[@]}"; do
  src="${SOURCE_CLAUDE}/commands/${command}"
  dest="${TARGET_CLAUDE}/commands/${command}"

  if [[ ! -f "$src" ]]; then
    warn "source command missing, skipping: ${command}"
    continue
  fi

  if [[ -e "$dest" && $FORCE -eq 0 ]]; then
    log "  skipped command ${command} (already present, use --force to replace)"
    skipped=$((skipped + 1))
    continue
  fi

  run cp "$src" "$dest"
  did install "command /${command%.md}"
  installed=$((installed + 1))
done

log ""
if [[ $DRY_RUN -eq 1 ]]; then
  log "Would install ${installed} item(s), skipping ${skipped}."
else
  log "Installed ${installed} item(s), skipped ${skipped}."
fi

if [[ $DRY_RUN -eq 0 ]] && command -v python3 >/dev/null 2>&1; then
  if [[ -f "${SOURCE_ROOT}/tools/ogenic/validate_toolkit.py" ]]; then
    log ""
    log "Validating the installed toolkit:"
    python3 "${SOURCE_ROOT}/tools/ogenic/validate_toolkit.py" --root "${TARGET_CLAUDE}" || \
      warn "validation reported problems, see above"
  fi
fi

log ""
log "Done. Start a new Claude Code session in ${TARGET_BASE%/} and run /god-mode."
