# TEST REPORT - MUHANNAD OS 1.0 (build-ready source, revision 3)
Environment used for these checks: Ubuntu 24.04 sandbox, 1 CPU, 3.9 GB RAM, **no internet, no /dev/kvm**, no live-build/debootstrap/xorriso/qemu/shellcheck, and no GitHub access.

**Overall status: NOT VERIFIED. No ISO has been built. The GitHub workflow has never been executed. Do not install on real hardware.**

| # | Area | Result | Evidence / notes |
|---|------|--------|------------------|
| 1 | Static source/config/workflow review (`tests/static_check.py`, 66 checks) | PASS | Code review only. Includes: YAML/dconf parse, package lists, workflow structure, safety settings, no destructive commands, <=95 files for web upload |
| 2 | Shell syntax (`bash -n`, all scripts/hooks) | PASS | shellcheck: NOT TESTED (not installed here; runs in CI `static` job at `-S error`) |
| 3 | Workflow YAML parses | PASS | Parse only. Not run on GitHub; `actionlint`: NOT TESTED |
| 4 | `screen_check.py` logic (synthetic frames) | PASS | Black frame, uniform frame, menu->desktop: correct verdicts. Real QEMU frames: NOT TESTED |
| 5 | Script guards (build.sh/verify-iso.sh/qemu test refuse cleanly when tools/ISO missing) | PASS | Exit codes 2/1/2 observed |
| 6 | Boot-splash assets (black bg, white logo, no text) | PASS (static) | Pixel/script inspection; real rendering NOT TESTED |
| 7 | Windows-safety review (manual-only partitioning, no EFI fallback overwrite, no destructive commands) | PASS (static) | Calamares runtime NOT TESTED. Version in bookworm may ignore `availableChoices` |
| 8 | Debian package names / availability | NOT TESTED | No apt index offline. First CI build will confirm (`calamares`, `calamares-settings-debian`, `gnome-shell-extension-dashtodock`, `fonts-inter`, `polkitd`, `libspa-0.2-bluetooth`, ...) |
| 9 | ISO build | BLOCKED | Needs network + live-build; run via GitHub Actions |
| 10 | ISO checksum / structure (`verify-iso.sh`) | BLOCKED | Needs ISO |
| 11 | UEFI boot in QEMU/OVMF | BLOCKED | Needs ISO + qemu. Automatic check is heuristic; human must view `final.png` |
| 12 | Desktop/apps/lock/login, installer, dual boot with Windows, Secure Boot, hardware, sleep | NOT TESTED | Needs running system / VM / hardware |
| 13 | Live-ISO Secure Boot | NOT TESTED (likely unsupported) | live-build GRUB is not shim-signed |
| 14 | Screenshots of running system | BLOCKED | Needs boot test |

## Fixes made in revision 2 (code review, not runtime-proven)
- `auto/build` masked `lb build` failures (pipe to tee) -> pipefail.
- `os-release`, GDM greeter file and Calamares settings/modules were shipped via includes and could clash with package-owned files -> installed by a chroot hook instead.
- Workflow was missing: python3-yaml (build.sh runs the tests), syslinux/isolinux/grub-efi-bin/mtools, disk-space cleanup, KVM enabling, correct OVMF vars handling, artifact of screenshots/logs.
- Scripts now invoked with `bash` (web upload/Windows zip lose exec bits); the exec-bit test was removed accordingly.
- verify-iso.sh EFI check pattern corrected; added size/kernel/initrd/BIOS/GPT checks.
- Recommends are off, so essential GNOME/audio/portal/polkit packages were listed explicitly.
- Added: .gitignore, .gitattributes (LF endings), optional Debian snapshot pinning, BUILD-INFO.txt and package manifest, GitHub Release job for `v*` tags.

## Revision 3 - beginner-flow review (still no ISO; nothing here is runtime-proven on GitHub)
| Item | Result | Notes |
|---|---|---|
| Static suite (66 checks) incl. workflow robustness, LF endings, file count, risky package names | PASS | code review level |
| `check-packages.sh` logic (fake apt-cache: missing pkg -> exit 1, all present -> exit 0) | PASS | Real check against Debian 12 index: NOT TESTED, runs in CI before the long build |
| Upload simulation (unzip == tracked files, `.github/workflows/build.yml` present, <100 files, no file >25 MB) | PASS | Real GitHub web upload: NOT TESTED |
| Workflow executed on GitHub Actions | NOT TESTED | never run |
| ISO build / verify / UEFI boot test / VirtualBox boot | BLOCKED / NOT TESTED | needs GitHub run and user's VM |
Fixes: `| tee` could hide failures in Actions (default shell had no pipefail) -> `defaults.run.shell: bash`; push-to-main auto-trigger removed (a half-finished upload could start a doomed build); `apt-get update` added before runner installs; `loupe` (not in Debian 12) -> `eog`; `live-*` packages removed (live-build adds them); dconf profile no longer shipped (owned by a Debian package); ISO BIOS/GPT checks demoted to warnings; shellcheck advisory; artifact folder layout documented; Arabic guide and workflow copy file added.
