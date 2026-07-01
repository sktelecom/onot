# Windows Test Handoff (for an automated agent session on a Windows PC)

This is a self-contained runbook. Run it on a clean Windows 10/11 x64 machine (a fresh
VM is ideal) with Microsoft Defender real-time protection ON. An automated agent session on
that machine can drive most of it; a human must do the parts marked "HUMAN ONLY"
(SmartScreen dialog, watching for a console-window flash, install/uninstall).

The goal is to close the one residual risk that CI cannot cover: does the real, fully
frozen, installed Windows app boot and work end to end? Issue #68 (blank screen) only
ever showed up in the actually-released Windows exe, so this pass matters.

## What is already proven (do not re-litigate)

CI on `windows-latest` already passes for this change (PR #77 on branch
`feat/windows-onboarding`):
- The packaged `file://` render path (no blank screen) and the in-app "Try a sample"
  parse flow, via the Playwright-electron E2E.
- The NSIS installer builds; core Python tests pass on Windows.

CI does NOT install and run the frozen installer, cannot see SmartScreen or antivirus
behavior, and runs the sidecar as dev Python (not the frozen `onot-sidecar.exe`). Those
are exactly what this pass verifies.

## What this pass verifies

1. The installed app boots with the UI rendered (no blank screen).
2. No console window flashes when the app or its sidecar starts (the `windowsHide` fix).
3. The frozen `onot-sidecar.exe` starts and becomes healthy; sample -> parse -> preview
   -> download all work, including PDF save.
4. SmartScreen and Defender behavior match the User Guide (HUMAN ONLY).
5. Install and uninstall are clean (HUMAN ONLY).
6. On failure, the app shows a Retry/Quit dialog naming a log file, not a silent quit.

## Prerequisites

- Clean Windows 10/11 x64, Defender on.
- A terminal or automation agent available in a working folder.
- Node.js 20+ (for the optional automated check).
- Either the GitHub CLI `gh` authenticated to `sktelecom/onot`, or a browser to reach
  the repo Actions/Releases pages.

## Step 1. Get a testable installer

Pick ONE. Option A is fastest for functional testing. Option A-MOTW or Option C is
required to observe the real SmartScreen prompt (SmartScreen only fires on files that
carry the internet Mark-of-the-Web).

Option A (fast, functional): download the CI build artifact via `gh`.
```
gh run list -R sktelecom/onot --branch feat/windows-onboarding --workflow ci.yml --limit 1
gh run download <run-id> -R sktelecom/onot -n onot-windows-latest -D onot-artifact
```
The exe is inside `onot-artifact\dist-electron\`. Note the local filename is
`onot Setup <version>.exe` (with spaces). That is the same binary users get; GitHub only
renames it to `onot-Setup-<version>.exe` when it is published to a Release. Files fetched
with `gh` carry no Mark-of-the-Web, so SmartScreen will not prompt on this copy.

Option A-MOTW (to see SmartScreen too): from a browser, open the same CI run's Summary
page, download the `onot-windows-latest` artifact zip, and extract it with Windows
Explorer (right-click, Extract All). Explorer propagates the Mark-of-the-Web to the exe,
so double-clicking it triggers SmartScreen like a real download.

Option C (most faithful): ask the maintainer to push a prerelease tag (for example
`v1.1.2-rc.1`); `release.yml` publishes it as a GitHub prerelease. Download
`onot-Setup-1.1.2-rc.1.exe` from the Releases page in a browser. This is the exact
artifact and download path a real user hits.

## Step 2. Install and first launch (HUMAN ONLY for SmartScreen)

1. Double-click the installer.
2. If SmartScreen shows "Windows protected your PC" / unknown publisher: click
   "More info", then "Run anyway". Confirm the User Guide wording matches. (Only fires
   for Option A-MOTW or C.)
3. If Defender quarantines it, restore it from quarantine (or add an exception) and run
   again. Note whether this happened.
4. Let the one-click installer finish. Confirm a Start-menu entry and desktop shortcut,
   and an uninstall entry under Windows Settings, Apps, Installed apps.
5. The app auto-launches. WATCH THE SCREEN AS IT STARTS: note whether any black console
   window flashes even briefly (it should not). This is the `windowsHide` check and it
   cannot be automated.

## Step 3. Automated boot + flow check (an agent can run this)

This launches the REAL installed exe with Playwright-electron and checks the frozen app
boots, renders, and completes the sample flow. It exercises the frozen sidecar and the
`file://` render on the actual binary.

First, find the installed exe (do not assume the path):
```
where /r "%LOCALAPPDATA%\Programs" onot.exe
```
Use the Start-menu shortcut target if the search is ambiguous. Then, in a scratch folder:
```
npm init -y
npm i -D @playwright/test
```
Create `boot-check.mjs` (set ONOT_EXE to the path found above):
```js
import { _electron as electron } from "@playwright/test";

const exe = process.env.ONOT_EXE; // full path to the installed onot.exe
const app = await electron.launch({ executablePath: exe, args: [] });
const win = await app.firstWindow();
const errors = [];
win.on("console", (m) => m.type() === "error" && errors.push(m.text()));

await win.getByText("OSS Notice Generator").waitFor({ timeout: 120000 }); // renders (no blank screen)
const proto = await win.evaluate(() => window.location.protocol);
await win.getByTestId("try-sample").click();                              // bundled sample
await win.getByText("example-product").waitFor({ timeout: 60000 });        // frozen sidecar parsed it

console.log("protocol:", proto);
console.log("ERR_FILE_NOT_FOUND:", errors.filter((e) => /ERR_FILE_NOT_FOUND/i.test(e)).length);
console.log("BOOT_CHECK_PASS");
await app.close();
```
Run it:
```
set ONOT_EXE=C:\path\to\onot.exe
node boot-check.mjs
```
Pass criteria: it prints `protocol: file:`, `ERR_FILE_NOT_FOUND: 0`, and
`BOOT_CHECK_PASS`. A hang at the first `waitFor` means a blank screen or a sidecar that
never became healthy — capture the log (Step 5) in that case.

## Step 4. Manual in-app checks (HUMAN, quick)

With the app open:
- Click "Try a sample": `example-product` and a component count appear.
- Click the drop area: the file chooser is filtered toward SBOM types. Drag a file in too.
- Uncheck every output format: the "select at least one output format" hint shows;
  re-check html.
- Click "Generate preview"; then download WITHOUT previewing first (both should work).
- Download html, text, markdown: files save with sensible names.
- Download pdf: a Save dialog appears; cancel it once (a "PDF save cancelled" note
  appears); save it once (a valid PDF is written).
- Upload a random `.json` that is not an SBOM: a readable error with a recovery hint
  appears.

## Step 5. Diagnostics an agent can gather

- Sidecar log (created on every start): search for it, then read the tail.
  ```
  where /r "%APPDATA%" sidecar.log
  ```
  (userData is typically `%APPDATA%\onot\sidecar.log`; do not assume, search for it.)
- No orphan sidecar after quitting the app:
  ```
  tasklist | findstr /i "onot-sidecar onot.exe"
  ```
  Close the app, wait a few seconds, run it again; both should be gone.
- To exercise the failure dialog (Step 6 of the checklist): rename or block
  `onot-sidecar.exe` in the install folder and launch the app; it should show a
  Retry/Quit dialog that names the log path, not quit silently.

## Step 6. Uninstall (HUMAN)

Uninstall via Windows Settings, Apps, Installed apps, or the Start-menu uninstaller.
Confirm the app is removed cleanly.

## Report back with this template

```
onot Windows test — build source: [Option A / A-MOTW / C], version: <x.y.z>
1. Install + SmartScreen: [ok / issue] (SmartScreen shown: yes/no; wording matched: yes/no)
2. Defender quarantine: [none / happened + restored]
3. Console-window flash on launch: [none / flashed]
4. boot-check.mjs: [BOOT_CHECK_PASS / failed at <step>], protocol=<>, ERR_FILE_NOT_FOUND=<n>
5. In-app flow (sample, formats hint, preview-optional, html/text/md, pdf save+cancel, error hint): [all ok / list issues]
6. Failure dialog (Retry/Quit + log path): [ok / issue / not tested]
7. Orphan sidecar after quit: [none / found]
8. Uninstall: [clean / issue]
Notes / screenshots: <...>
```

See `docs/WINDOWS_QA_CHECKLIST.md` for the condensed checklist this runbook implements.
