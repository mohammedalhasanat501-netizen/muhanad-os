#!/bin/bash
set -uo pipefail
cd "$(dirname "$0")/.."
rc=0
for f in scripts/*.sh auto/* config/hooks/live/* config/includes.chroot/usr/local/bin/*; do
  bash -n "$f" || { echo "SYNTAX FAIL: $f"; rc=1; }
done
if command -v shellcheck >/dev/null; then
  if ! shellcheck -S error scripts/*.sh auto/*; then
    if [ "${SHELLCHECK_BLOCKING:-0}" = "1" ]; then rc=1; else echo "ADVISORY: shellcheck reported issues (non-blocking by default)"; fi
  fi
else echo "NOTE: shellcheck not installed (skipped)"; fi
exit $rc
