#!/bin/bash
# Build the MUHANNAD OS ISO. Run as root on Debian 12 (bookworm) - or in the CI container.
# Optional env: SNAPSHOT=YYYYMMDDTHHMMSSZ  -> pin all Debian packages to snapshot.debian.org at that instant
set -euo pipefail
cd "$(dirname "$0")/.."
[ "$(id -u)" -eq 0 ] || { echo "ERROR: run as root (sudo bash scripts/build.sh)"; exit 1; }
for t in lb debootstrap xorriso mksquashfs python3; do
  command -v "$t" >/dev/null || { echo "ERROR: missing tool: $t (apt install live-build debootstrap xorriso squashfs-tools)"; exit 2; }
done
python3 -c 'import yaml' 2>/dev/null || { echo "ERROR: python3-yaml missing"; exit 2; }

chmod +x config/hooks/live/*.hook.chroot config/includes.chroot/usr/local/bin/* auto/* scripts/*.sh scripts/*.py tests/*.py
python3 scripts/gen-assets.py
python3 tests/static_check.py

# Reproducibility: fixed timestamps from the git commit when available
if git rev-parse HEAD >/dev/null 2>&1; then
  SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)"; COMMIT="$(git rev-parse HEAD)"
else
  SOURCE_DATE_EPOCH="$(date +%s)"; COMMIT="unknown"
fi
export SOURCE_DATE_EPOCH LB_SOURCE_DATE_EPOCH="$SOURCE_DATE_EPOCH"

EXTRA=()
if [ -n "${SNAPSHOT:-}" ]; then
  M="http://snapshot.debian.org/archive/debian/${SNAPSHOT}/"
  EXTRA+=(--parent-mirror-bootstrap "$M" --parent-mirror-chroot "$M" --parent-mirror-binary "$M" \
          --mirror-bootstrap "$M" --mirror-chroot "$M" --mirror-binary "$M" --security false --updates false)
  echo "Pinned to Debian snapshot $SNAPSHOT"
fi

lb clean >/dev/null 2>&1 || true
lb config "${EXTRA[@]}"
lb build

ISO="$(ls -1 ./*.iso 2>/dev/null | head -n1 || true)"
[ -n "$ISO" ] || { echo "ERROR: lb build finished but no ISO was produced"; exit 3; }
[ "$(stat -c %s "$ISO")" -gt 500000000 ] || { echo "ERROR: ISO suspiciously small"; exit 4; }

mkdir -p release
mv "$ISO" release/muhannad-os-1.0-amd64.iso
cp -f ./*.packages ./*.contents release/ 2>/dev/null || true
{
  echo "commit=$COMMIT"; echo "source_date_epoch=$SOURCE_DATE_EPOCH"; echo "snapshot=${SNAPSHOT:-none (latest bookworm)}"
  echo "live-build=$(lb --version 2>/dev/null || echo unknown)"; echo "built=$(date -u +%FT%TZ)"
} > release/BUILD-INFO.txt
( cd release && sha256sum muhannad-os-1.0-amd64.iso > SHA256SUMS && cat SHA256SUMS )
echo "Built release/muhannad-os-1.0-amd64.iso (NOT yet verified - run scripts/verify-iso.sh and the boot test)"
