# Troubleshooting
- **Boot menu doesn't show Windows**: run `sudo os-prober && sudo update-grub`. Windows must be mounted/visible; NTFS must not be hibernated.
- **Live USB will not boot with Secure Boot on**: disable Secure Boot temporarily to run the installer.
- **No Wi-Fi**: non-free firmware is bundled (iwlwifi, realtek, atheros); other chips may need extra `firmware-*` packages.
- **Black screen after splash**: add `nomodeset` at the GRUB prompt once, then install the vendor GPU driver.
- **Secure Boot refuses to boot**: confirm the ISO checksum; temporarily disable Secure Boot to isolate.
- **Installer shows other partition modes**: your Calamares version ignores `availableChoices`; use Manual only.
