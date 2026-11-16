# Installation (simple version)
1. **First read `DUAL-BOOT.md` and complete its Windows checklist** (backup, BitLocker key, free space).
2. Verify the ISO: `sha256sum -c SHA256SUMS`.
3. Write the ISO to a USB stick (Rufus in DD mode, balenaEtcher, or `dd` - double-check the target is the USB stick).
4. Boot the USB in UEFI mode. **Secure Boot:** the live USB may not boot with Secure Boot ON (untested); if it does not, turn Secure Boot off in firmware just to run the installer. The installed system uses Debian's signed shim. Open a terminal and run `sudo muhannad-preflight` (read-only) to see disks, EFI partition and free space.
5. Start the installer. Pick language/keyboard, then **Manual partitioning** (the only option offered).
6. Create your partitions **only inside free/unallocated space**. Mount the **existing** EFI partition at `/boot/efi` and leave **Format unchecked**.
7. Check the installer Summary page: nothing Windows-related may be listed as formatted/deleted/resized. If it is, press Cancel.
8. Install, reboot, choose MUHANNAD OS or Windows in the boot menu.
Try everything first in a virtual machine (VirtualBox/QEMU) before real hardware.
