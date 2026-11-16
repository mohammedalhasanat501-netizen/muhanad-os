#!/usr/bin/env python3
"""Offline static checks. Prints PASS/FAIL per check. These are CODE-REVIEW level checks,
NOT runtime tests. Exit code 1 if any FAIL."""
import os, re, struct, zlib, subprocess, configparser, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
results = []
def check(name, ok, detail=""):
    results.append(ok); print(("PASS" if ok else "FAIL") + ": " + name + (f"  [{detail}]" if detail and not ok else ""))

def read(p): return open(p, encoding="utf-8").read()
def png_pixels(path):
    d = open(path, "rb").read(); assert d[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, ihdr = 8, b"", None
    while pos < len(d):
        n = struct.unpack(">I", d[pos:pos+4])[0]; t = d[pos+4:pos+8]; b = d[pos+8:pos+8+n]
        if t == b"IHDR": ihdr = struct.unpack(">IIBBBBB", b)
        if t == b"IDAT": idat += b
        pos += 12 + n
    w, h, _, ct, *_ = ihdr; raw = zlib.decompress(idat); bpp = {6: 4, 2: 3}[ct]
    rows = [raw[i*(w*bpp+1)+1:(i+1)*(w*bpp+1)] for i in range(h)]
    return w, h, bpp, rows

required = ["auto/config","auto/build","tests/screen_check.py","GITHUB-QUICKSTART.md","GUIDE-AR.md","GITHUB-WORKFLOW-COPY.txt","scripts/check-packages.sh",".gitignore",".gitattributes","scripts/build.sh","scripts/verify-iso.sh","scripts/qemu-smoke-test.sh",
 ".github/workflows/build.yml","config/package-lists/base.list.chroot","config/package-lists/desktop.list.chroot",
 "config/package-lists/installer.list.chroot","config/includes.chroot/usr/share/muhannad/calamares/settings.conf",
 "config/includes.chroot/usr/share/muhannad/calamares/modules/partition.conf","config/includes.chroot/etc/dconf/db/local.d/00-muhannad",
 "config/includes.chroot/usr/share/plymouth/themes/muhannad/muhannad.script","config/includes.chroot/usr/local/bin/muhannad-preflight"] + \
 [f"{n}.md" for n in ["README","BUILD","INSTALLATION","DUAL-BOOT","TROUBLESHOOTING","SECURITY","TEST-REPORT","RELEASE-NOTES"]]
missing = [f for f in required if not os.path.exists(f)]
check("required files exist", not missing, str(missing))

# shell syntax
bad = []
for f in glob.glob("scripts/*.sh")+glob.glob("auto/*")+glob.glob("config/hooks/live/*")+["config/includes.chroot/usr/local/bin/muhannad-preflight"]:
    if subprocess.run(["bash","-n",f],capture_output=True).returncode: bad.append(f)
check("shell scripts pass bash -n", not bad, str(bad))
check("build.sh sets exec bits itself (web uploads lose them)", "chmod +x config/hooks/live" in read("scripts/build.sh"))

# package lists
pk = []
for f in glob.glob("config/package-lists/*.chroot"):
    for line in read(f).splitlines():
        if line.strip().startswith("#"): continue
        pk += line.split()
dups = {p for p in pk if pk.count(p) > 1}
check("no duplicate packages", not dups, str(dups))
check("no malformed package tokens", all(re.fullmatch(r"[a-z0-9][a-z0-9+.\-]*", p) for p in pk), str([p for p in pk if not re.fullmatch(r"[a-z0-9][a-z0-9+.\-]*", p)]))
for need in ["shim-signed","grub-efi-amd64-signed","os-prober","calamares","plymouth","gdm3","network-manager","bluez","pipewire","firefox-esr","nautilus","gnome-software"]:
    check(f"package present: {need}", need in pk)

# dconf keyfile parse
cp = configparser.ConfigParser(interpolation=None); cp.optionxform = str
try: cp.read("config/includes.chroot/etc/dconf/db/local.d/00-muhannad"); ok = len(cp.sections()) > 3
except Exception as e: ok = False
check("dconf keyfile parses", ok)
for p in re.findall(r"file://(/usr/share/[^']+)", read("config/includes.chroot/etc/dconf/db/local.d/00-muhannad")):
    check(f"wallpaper path exists in includes: {p}", os.path.exists("config/includes.chroot"+p))

# YAML
try:
    import yaml
    for f in glob.glob("config/includes.chroot/usr/share/muhannad/calamares/**/*.conf", recursive=True)+glob.glob("config/includes.chroot/etc/calamares/**/*.desc", recursive=True):
        yaml.safe_load(read(f))
    check("Calamares YAML parses", True)
    part = yaml.safe_load(read("config/includes.chroot/usr/share/muhannad/calamares/modules/partition.conf"))
    check("SAFETY: partitioning is manual-only", part.get("availableChoices")==["manual"] and part.get("initialPartitioningChoice")=="none")
    boot = yaml.safe_load(read("config/includes.chroot/usr/share/muhannad/calamares/modules/bootloader.conf"))
    check("SAFETY: EFI fallback path not overwritten", boot.get("installEFIFallback") is False)
    check("bootloader entry is MUHANNAD (not Windows)", boot.get("efiBootloaderId")=="MUHANNAD")
except ImportError:
    check("Calamares YAML parses (python3-yaml missing)", False, "install python3-yaml")

# boot splash: black bg + only a centered white logo
s = read("config/includes.chroot/usr/share/plymouth/themes/muhannad/muhannad.script")
check("splash background pure black", "SetBackgroundTopColor(0.0, 0.0, 0.0)" in s and "SetBackgroundBottomColor(0.0, 0.0, 0.0)" in s)
check("splash has no text elements", not re.search(r"Image\.Text|Text\(", s))
w,h,bpp,rows = png_pixels("config/includes.chroot/usr/share/plymouth/themes/muhannad/logo.png")
op = [r[i+3] for r in rows for i in range(0,len(r),4) if r[i+3]>0]
white = all(r[i]==255 and r[i+1]==255 and r[i+2]==255 for r in rows for i in range(0,len(r),4) if r[i+3]>0)
check("logo is pure white (#FFFFFF) with transparency", white and len(op)>1000)
check("logo is not the Apple logo (trademark placeholder policy documented)", "NOT included" in read("scripts/gen-assets.py"))

# Windows-safety review: no destructive disk commands in any shipped script/config
danger = re.compile(r"\b(mkfs\S*|wipefs|sgdisk|sfdisk|fdisk|parted\s+\S+\s+(mkpart|rm|resize)|dd\s+.*of=/dev|efibootmgr\s+.*(-B|-c|-o)|shred|blkdiscard)\b")
hits = []
for f in glob.glob("scripts/*.sh")+glob.glob("auto/*")+glob.glob("config/hooks/live/*")+["config/includes.chroot/usr/local/bin/muhannad-preflight"]:
    for i,l in enumerate(read(f).splitlines(),1):
        if l.strip().startswith("#"): continue
        if danger.search(l): hits.append(f"{f}:{i}")
check("SAFETY: no destructive disk/EFI commands in scripts", not hits, str(hits))
check("os-prober enabled for dual-boot menu", "GRUB_DISABLE_OS_PROBER=false" in read("config/includes.chroot/etc/default/grub.d/10-muhannad.cfg"))
check("GRUB menu timeout shown", "GRUB_TIMEOUT_STYLE=menu" in read("config/includes.chroot/etc/default/grub.d/10-muhannad.cfg"))

# ---- build-chain / workflow review ----
check("auto/build uses pipefail (failures not masked by tee)", "pipefail" in read("auto/build"))
check("no package-owned conffiles shipped via includes (os-release, gdm3, calamares settings/modules)",
      not os.path.exists("config/includes.chroot/etc/os-release") and not os.path.exists("config/includes.chroot/etc/gdm3") and not os.path.exists("config/includes.chroot/etc/calamares/settings.conf") and not os.path.exists("config/includes.chroot/etc/calamares/modules"))
h = read("config/hooks/live/0010-branding.hook.chroot")
check("hook installs calamares overrides + os-release + plymouth + dconf", all(k in h for k in ["/etc/calamares/settings.conf","/usr/lib/os-release","plymouth-set-default-theme","dconf update"]))
try:
    import yaml as _y
    wf = _y.safe_load(read(".github/workflows/build.yml")); jobs = wf["jobs"]
    check("workflow has static+build jobs", "static" in jobs and "build" in jobs)
    steps = " ".join(str(x.get("run","")) + str(x.get("uses","")) for x in jobs["build"]["steps"])
    for k in ["scripts/build.sh","verify-iso.sh","qemu-smoke-test.sh","upload-artifact","python3-yaml","live-build","debootstrap","xorriso","mtools","isolinux","grub-efi-amd64-bin","ovmf","socat","SHA256SUMS"]:
        check(f"workflow references: {k}", k in steps)
    check("workflow calls scripts via bash (no reliance on exec bits)", not re.search(r"(^|\s)\./scripts/", steps))
    check("workflow ISO build container is debian:bookworm", "debian:bookworm" in steps)
    check("workflow supports workflow_dispatch (manual Run button)", "workflow_dispatch" in (wf.get("on") or wf.get(True)))
except Exception as e:
    check("workflow YAML review", False, str(e))
SKIP={".git","__pycache__","chroot","binary","cache",".build","release","test-output"}
nfiles = sum(len(f) for r,d,f in os.walk(".") if not (SKIP & set(r.split(os.sep))))
check("project has <= 95 files (GitHub web upload limit is 100 per upload)", nfiles <= 95, str(nfiles))
bs = read("scripts/build.sh")
check("build.sh refuses to run without root/tools and rejects tiny ISOs", "run as root" in bs and "suspiciously small" in bs)
check("qemu test uses a disposable qcow2 + read-only ISO only", "disposable.qcow2" in read("scripts/qemu-smoke-test.sh") and "readonly=on" in read("scripts/qemu-smoke-test.sh"))

# ---- beginner-flow / robustness checks ----
check("package lists avoid risky names (loupe not in Debian 12; live-* installed by live-build itself)",
      "loupe" not in pk and not any(x.startswith("live-") for x in pk), str([x for x in pk if x=="loupe" or x.startswith("live-")]))
check("fail-fast package checker exists and is used by workflow", os.path.exists("scripts/check-packages.sh") and "check-packages.sh" in read(".github/workflows/build.yml"))
try:
    _on = wf.get("on") or wf.get(True)
    check("workflow: default shell is bash (pipefail) so '| tee' cannot hide failures", wf.get("defaults",{}).get("run",{}).get("shell")=="bash")
    check("workflow: no auto-run on push to main (manual Run workflow button + tags only)", "branches" not in (_on.get("push") or {}))
    check("workflow: has manual trigger", "workflow_dispatch" in _on)
    check("workflow: apt-get update before installing on runner", read(".github/workflows/build.yml").count("apt-get update") >= 4)
except Exception as e:
    check("workflow robustness review", False, str(e))
check("GITHUB-WORKFLOW-COPY.txt is identical to .github/workflows/build.yml", read("GITHUB-WORKFLOW-COPY.txt") == read(".github/workflows/build.yml"))
check("dconf profile not shipped (owned by dconf-gsettings-backend); hook ensures system-db:local", not os.path.exists("config/includes.chroot/etc/dconf/profile") and "system-db:local" in read("config/hooks/live/0010-branding.hook.chroot"))
crlf = [f for f in glob.glob("**/*", recursive=True) if os.path.isfile(f) and not f.endswith((".png",".zip")) and b"\r" in open(f,"rb").read()]
check("all text files use LF line endings", not crlf, str(crlf))
big = [f for f in glob.glob("**/*", recursive=True) if os.path.isfile(f) and os.path.getsize(f) > 20*1024*1024]
check("no file over 20 MB (web upload limit is 25 MB)", not big, str(big))
print(f"\n{sum(results)}/{len(results)} checks passed"); sys.exit(0 if all(results) else 1)
