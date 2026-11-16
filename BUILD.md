# Building
## Option A - GitHub Actions (recommended)
Push to GitHub; `.github/workflows/build.yml` builds in a `debian:bookworm` container, verifies the ISO, boot-tests it in QEMU/OVMF on a disposable disk, and uploads `release/` (ISO + `SHA256SUMS`).
## Option B - local (Debian 12 or Ubuntu with root, ~25 GB free, internet)
```
sudo apt install live-build debootstrap xorriso squashfs-tools python3 python3-yaml
sudo bash scripts/build.sh
bash scripts/verify-iso.sh
```
Output: `release/muhannad-os-1.0-amd64.iso`, `release/SHA256SUMS`.
Optional: `SNAPSHOT=20261110T000000Z sudo -E bash scripts/build.sh` pins every Debian package to snapshot.debian.org at that instant (and disables rolling security/updates repos) for a repeatable package set. Without it you get the latest bookworm packages; `release/BUILD-INFO.txt` and the `.packages` manifest record what was used.
Reproducibility limits: container image `debian:bookworm` and GitHub actions are version-tagged, not hash-pinned; the ISO is not bit-for-bit reproducible.
## Beginners
Use `GITHUB-QUICKSTART.md`.
## Tests
`python3 tests/static_check.py` (offline static checks), `bash scripts/lint.sh`, `bash scripts/qemu-smoke-test.sh` (needs qemu + ovmf + socat; uses a throwaway qcow2 disk only).
## Before publishing
Replace `CHANGE-ME` URLs in `branding.desc` and `os-release`.
