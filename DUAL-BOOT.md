# Dual boot and Windows protection
## Design guarantees (by configuration, still need runtime verification)
- Installer offers **manual partitioning only**; no automatic erase/replace/resize.
- Bootloader ID is `MUHANNAD`; `installEFIFallback: false` so `\EFI\BOOT\bootx64.efi` is not overwritten.
- GRUB uses `os-prober` and always shows the menu (8 s) so Windows appears alongside MUHANNAD OS.
- No project script formats, resizes, or repartitions disks (enforced by a static test).
## Limitation (honest)
Calamares cannot technically *prevent* a user from ticking "format" on the Windows EFI partition or deleting a Windows partition in manual mode. Safety therefore depends on following the steps and reading the Summary page. If you want zero risk, create the free space beforehand from Windows Disk Management and use a disposable VM first.
## Windows-side checklist (do this in Windows)
1. Back up personal files to an external drive.
2. **BitLocker/Device Encryption**: Settings > Privacy & security > Device encryption, or `manage-bde -status`. Save the recovery key from https://aka.ms/myrecoverykey. Changing boot settings can trigger a recovery-key prompt.
3. Disable Fast Startup (Power Options) and fully shut down (not hibernate).
4. Shrink the C: volume in Disk Management to create **unallocated** space (do this in Windows, not Linux).
5. Check Secure Boot state (`msinfo32`). Debian's signed shim works with Secure Boot on.
## Recovery: boot menu missing / Windows won't start
- Enter firmware boot menu (F12/Esc/F2/Del) and select "Windows Boot Manager" - it is untouched.
- From Windows (admin cmd): `bcdboot C:\Windows /s <ESP letter>:` restores the Windows entry.
- To restore the GRUB menu: boot the MUHANNAD live USB, mount the install, `grub-install` and `update-grub` in a chroot.
- If BitLocker asks for a key, enter the saved recovery key.
- Never run `bootrec /fixmbr` on a UEFI/GPT system.
