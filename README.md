# MUHANNAD OS

An independent, Debian 12 (bookworm)-based Linux distribution with a dark, macOS-inspired GNOME desktop,
a minimal black boot splash, and a **safety-first dual-boot installer** (Calamares, manual partitioning only).

> **Status: source-complete, NOT yet built or boot-tested.** See `TEST-REPORT.md` for exactly what has and has not been verified.

## Architecture (why)
- **Debian stable + live-build**: reproducible, long-supported, official Secure Boot chain (`shim-signed` + signed GRUB).
- **GNOME + Dash to Dock**: mature, Wayland-capable, gives top bar, dock, Control Center (quick settings), notifications, Wi-Fi/Bluetooth/sound/brightness, lock/login (GDM), workspaces and search without reinventing them. Styled via dconf defaults (dark navy/black, Inter font, Papirus icons).
- **Calamares installer**, restricted to manual partitioning, EFI fallback path never overwritten.
- **PipeWire, NetworkManager, BlueZ, ufw, AppArmor, unattended-upgrades**.
- Apps: Firefox ESR, Files, Terminal, Text Editor, Loupe, Videos, Software, System Monitor, File Roller, Screenshot.

## Boot logo / trademark note
The spec asks for an Apple logo. The Apple logo is Apple's trademark and no license is held, so it is **not** included.
A neutral white ring mark is generated instead. To use a logo you are legally authorized to use, replace
`config/includes.chroot/usr/share/plymouth/themes/muhannad/logo.png` (white on transparent) and edit `scripts/gen-assets.py`.
The OS identifies itself as MUHANNAD OS and makes no claim of Apple affiliation.

## Quick start
Beginners: `GUIDE-AR.md` (Arabic, full) or `GITHUB-QUICKSTART.md` (English). Otherwise see `BUILD.md` (build) and `INSTALLATION.md` / `DUAL-BOOT.md` (install). Never install on real hardware without reading `DUAL-BOOT.md`.
