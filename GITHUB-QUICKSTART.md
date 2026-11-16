# GitHub quick-start for beginners (Windows)
Nothing here touches your computer's disks or Windows. GitHub builds the ISO on its own servers.

## A. Create the repository
1. Go to https://github.com/signup and make a free account (skip if you have one).
2. Click the **+** (top right) > **New repository**.
3. Repository name: `muhannad-os`. Choose **Public** (recommended: free build minutes, faster boot test). Do **not** tick "Add a README". Click **Create repository**.

## B. Upload the project
1. Unzip `muhannad-os-source.zip` (right-click > **Extract All**). Open the extracted `muhannad-os` folder. Inside you should see: `auto`, `branding`, `config`, `scripts`, `tests`, `.github`, and files like `README.md`.
2. On your new GitHub page click the link **uploading an existing file**.
3. In File Explorer press **Ctrl+A** *inside* the `muhannad-os` folder (select everything in it - not the folder itself) and **drag** it into the GitHub page. Wait until all files finish uploading (about 50 files).
4. Leave "Commit directly to the main branch" selected and click **Commit changes**.
5. **Check:** on the repository page you must see a folder named `.github`. If it is missing:
   - click **Add file > Create new file**; in the name box type exactly `.github/workflows/build.yml` (typing `/` makes folders);
   - open `muhannad-os\.github\workflows\build.yml` from your computer in Notepad, copy everything, paste into GitHub, click **Commit changes**.

## C. Start the build
**The build does not start by itself after upload - you start it.**
1. Click the **Actions** tab. If you see a green button "I understand my workflows, go ahead and enable them", click it.
2. In the left list click **Build MUHANNAD OS ISO**.
3. Click **Run workflow** (grey dropdown on the right) > leave the boxes empty > green **Run workflow**.
4. Click the new run to watch it. It takes roughly 40-120 minutes. Green check = every step passed. Red X = something failed.

## D. Get the result
1. Open the finished run and scroll to **Artifacts** at the bottom. Download `muhannad-os-iso` and unzip it.
2. Inside: folder `release` (`muhannad-os-1.0-amd64.iso`, `SHA256SUMS`, `BUILD-INFO.txt`) and folder `test-output` (`early.png`, `final.png` screenshots, `boot-test.log`). Artifacts are kept for 14 days. **Open `final.png` yourself** - the automatic check is only a heuristic.
3. Check the file is intact: open PowerShell in the `release` folder and run
   `Get-FileHash .\muhannad-os-1.0-amd64.iso -Algorithm SHA256`
   The value must equal the one in `SHA256SUMS`.

## E. If the run is red
Click the failed (red) step, copy the last ~60 lines of its log, and send them to me. Failures on a first build are normal (for example a Debian package name that differs); they are usually one-line fixes.

## F. Safety rules
- Do **not** write the ISO to a USB stick or install it until a VM test (VirtualBox/QEMU) works and you have read `DUAL-BOOT.md`.
- Never choose "erase disk". This installer only offers manual partitioning; back up Windows first and save your BitLocker recovery key.

## G. Arabic guide with VirtualBox steps
See `GUIDE-AR.md`.
