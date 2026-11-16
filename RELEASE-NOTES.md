# Release notes - 1.0 (source, build-ready, unbuilt)
- Complete live-build source, GNOME dark/navy desktop defaults, black Plymouth splash with a neutral white logo, Calamares manual-only installer, GitHub Actions build + verify + UEFI boot test, docs.
- **No ISO exists yet.** First step: follow `GITHUB-QUICKSTART.md`.
- Apple logo not shipped (trademark); replace `logo.png` with an asset you are authorized to use.
## Known limitations
- Hardware, sleep/resume, Secure Boot, Windows dual-boot and Calamares behaviour are untested. Live USB may require Secure Boot off.
- Calamares cannot technically block a user from formatting Windows partitions in manual mode (see `DUAL-BOOT.md`).
- First CI build may reveal package-name or config errors to fix.
