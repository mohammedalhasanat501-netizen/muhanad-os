#!/bin/bash
# Fails in ~1 minute (instead of after a long build) if any package name in config/package-lists/ does not exist in Debian bookworm.
# Run inside a debian:bookworm container.  CHECK_ADD_COMPONENTS=1 adds contrib/non-free/non-free-firmware.
set -uo pipefail
cd "$(dirname "$0")/.."
command -v apt-cache >/dev/null || { echo "BLOCKED: apt-cache not available (run inside debian:bookworm)"; exit 2; }
if [ "${CHECK_ADD_COMPONENTS:-0}" = "1" ]; then
  cat > /etc/apt/sources.list.d/extra-components.sources <<'SRC'
Types: deb
URIs: http://deb.debian.org/debian
Suites: bookworm bookworm-updates
Components: contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
SRC
  apt-get update -qq || { echo "BLOCKED: apt-get update failed"; exit 2; }
fi
mapfile -t PK < <(grep -hv '^[[:space:]]*#' config/package-lists/*.list.chroot | tr -s ' \t' '\n' | grep -v '^$' | sort -u)
missing=()
for p in "${PK[@]}"; do apt-cache show "$p" >/dev/null 2>&1 || missing+=("$p"); done
echo "Checked ${#PK[@]} package names."
if [ ${#missing[@]} -gt 0 ]; then echo "FAIL: not found in Debian bookworm: ${missing[*]}"; exit 1; fi
echo "PASS: all package names exist"
