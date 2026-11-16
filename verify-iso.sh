#!/bin/bash
# Integrity + structure checks on a built ISO. Exit non-zero on any failure. Read-only.
set -uo pipefail
ISO="${1:-release/muhannad-os-1.0-amd64.iso}"
[ -f "$ISO" ] || { echo "FAIL: $ISO not found"; exit 1; }
command -v xorriso >/dev/null || { echo "BLOCKED: xorriso not installed"; exit 2; }
fail=0
ok(){ echo "PASS: $1"; }; ko(){ echo "FAIL: $1"; fail=1; }; warn(){ echo "WARN: $1 (not fatal; check manually)"; }

DIR="$(dirname "$ISO")"
if [ -f "$DIR/SHA256SUMS" ] && ( cd "$DIR" && sha256sum -c SHA256SUMS ); then ok "sha256 checksum matches SHA256SUMS"; else ko "sha256 checksum"; fi
[ "$(stat -c %s "$ISO")" -gt 500000000 ] && ok "ISO size > 500 MB" || ko "ISO size"

LIST="$(xorriso -indev "$ISO" -find / -type f 2>/dev/null || true)"
EL="$(xorriso -indev "$ISO" -report_el_torito plain 2>/dev/null || true)"
SA="$(xorriso -indev "$ISO" -report_system_area plain 2>/dev/null || true)"
echo "$LIST" | grep -q 'filesystem.squashfs'      && ok "live squashfs present"          || ko "live squashfs"
echo "$LIST" | grep -Eq '/live/vmlinuz'           && ok "kernel present"                 || ko "kernel"
echo "$LIST" | grep -Eq '/live/initrd'            && ok "initrd present"                 || ko "initrd"
echo "$LIST" | grep -Eqi 'efi'                    && ok "EFI files present"              || ko "EFI files"
echo "$EL"   | grep -qi 'UEFI'                    && ok "El Torito UEFI boot entry"      || ko "El Torito UEFI entry"
echo "$EL"   | grep -qi 'BIOS'                    && ok "El Torito BIOS boot entry"      || warn "El Torito BIOS entry"
echo "$SA"   | grep -qi 'GPT'                     && ok "hybrid GPT present"             || warn "hybrid GPT"
echo "$LIST" | grep -q 'boot/grub'                && ok "GRUB config present"            || ko "GRUB config"
exit $fail
