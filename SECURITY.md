# Security
- Live ISO Secure Boot: NOT guaranteed (live-build's GRUB is not shim-signed). Installed system: Debian shim-signed + signed GRUB. Secure Boot chain: Debian `shim-signed` + signed GRUB (not tested on real hardware yet).
- Firewall `ufw` default-deny incoming; AppArmor enabled; unattended security updates.
- No default passwords; root login disabled in installer (`setRootPassword: false`); autologin off.
- Build scripts are read-only with respect to disks; ISO test runs only on disposable qcow2 disks.
- GitHub workflow pins no third-party actions beyond `actions/*`.
- Known gaps: no full-disk encryption preset, no reproducible-bits guarantee (apt snapshots not pinned), no pentest done. Report issues privately to the maintainer.
