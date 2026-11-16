#!/bin/bash
# UEFI boot smoke test in QEMU/OVMF. Uses ONLY a throwaway virtual disk and a read-only ISO. Never touches real disks.
# Usage: qemu-smoke-test.sh ISO OUTDIR      env: WAIT=seconds (default 150 KVM / 600 TCG)
set -euo pipefail
ISO="${1:-release/muhannad-os-1.0-amd64.iso}"; OUT="${2:-test-output}"
for t in qemu-system-x86_64 qemu-img socat python3; do command -v $t >/dev/null || { echo "BLOCKED: $t not installed"; exit 2; }; done
[ -f "$ISO" ] || { echo "FAIL: ISO not found"; exit 1; }
mkdir -p "$OUT"; rm -f "$OUT"/*.ppm "$OUT"/*.png "$OUT/mon.sock"
qemu-img create -f qcow2 "$OUT/disposable.qcow2" 30G >/dev/null

CODE=""; VARS=""
for c in /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd /usr/share/ovmf/OVMF_CODE.fd; do [ -f "$c" ] && CODE="$c" && break; done
for v in /usr/share/OVMF/OVMF_VARS_4M.fd /usr/share/OVMF/OVMF_VARS.fd /usr/share/ovmf/OVMF_VARS.fd; do [ -f "$v" ] && VARS="$v" && break; done
[ -n "$CODE" ] && [ -n "$VARS" ] || { echo "BLOCKED: OVMF (UEFI firmware) not installed - apt install ovmf"; exit 2; }
cp "$VARS" "$OUT/OVMF_VARS.fd"

if [ -w /dev/kvm ]; then ACCEL=kvm; WAIT="${WAIT:-150}"; else ACCEL=tcg; WAIT="${WAIT:-600}"; fi
echo "UEFI boot test: accel=$ACCEL wait=${WAIT}s"

qemu-system-x86_64 -machine q35,accel=$ACCEL -m 4096 -smp 2 -cpu max \
  -drive if=pflash,format=raw,readonly=on,file="$CODE" \
  -drive if=pflash,format=raw,file="$OUT/OVMF_VARS.fd" \
  -drive file="$OUT/disposable.qcow2",if=virtio \
  -drive file="$ISO",media=cdrom,readonly=on \
  -vga std -display none -serial file:"$OUT/serial.log" \
  -monitor unix:"$OUT/mon.sock",server,nowait -pidfile "$OUT/qemu.pid" -daemonize

shot(){ echo "screendump $OUT/$1.ppm" | socat - UNIX-CONNECT:"$OUT/mon.sock" >/dev/null; sleep 2; }
cleanup(){ echo quit | socat - UNIX-CONNECT:"$OUT/mon.sock" >/dev/null 2>&1 || true; }
trap cleanup EXIT

sleep 30;  shot early
sleep $(( WAIT > 30 ? WAIT - 30 : 1 )); shot final
python3 "$(dirname "$0")/../tests/screen_check.py" "$OUT/early.ppm" "$OUT/final.ppm"
