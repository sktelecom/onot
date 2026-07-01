# Windows First-Run QA Checklist

A manual pass that a real Windows user's journey must complete before a release is
considered verified. Automated CI covers the packaged `file://` render, unit behavior,
and installer naming, but SmartScreen, real antivirus behavior, and install/uninstall
can only be confirmed on a real machine.

Environment: a clean Windows 10 or 11 x64 machine (a fresh VM is ideal), with Microsoft
Defender real-time protection on. Record the app version tested.

## Download and install

- [ ] From the GitHub README, the desktop path is clear and nothing tells you to run
      `pip` for the desktop app.
- [ ] On the Releases page, there is a single obvious installer named
      `onot-Setup-<version>.exe` matching the User Guide.
- [ ] Downloading gives one self-contained `.exe`; no separate Python or runtime is needed.
- [ ] Double-clicking shows SmartScreen ("Windows protected your PC" / unknown publisher).
      **More info → Run anyway** installs it, exactly as the User Guide describes.
- [ ] If Defender quarantines the installer, the User Guide's restore/exception steps work.
- [ ] Install completes; Start-menu and desktop shortcuts exist; an uninstall entry appears
      under Settings → Apps → Installed apps.

## Launch

- [ ] The app window opens and the UI renders (no blank screen).
- [ ] No console window flashes when the app starts.
- [ ] The app becomes usable within a reasonable time even on the first launch (Defender
      scan). If startup fails, the error dialog offers **Retry**/**Quit** and names the log
      file (`%APPDATA%\onot\sidecar.log` under the app's userData path).

## Generate a notice

- [ ] "No SBOM yet?": clicking **Try a sample** loads the bundled example and shows
      `example-product` with its component count.
- [ ] Clicking the drop area opens a chooser filtered toward SBOM types; dragging a file
      onto the area also works.
- [ ] Unchecking every output format shows the "select at least one output format" hint
      instead of an empty area; re-checking restores the download buttons.
- [ ] **Generate preview** shows the notice; downloading works **without** previewing first.
- [ ] Downloading html, text, and markdown saves files with sensible names.
- [ ] **Download pdf** opens a Save dialog; cancelling it shows a "PDF save cancelled" note;
      saving produces a valid PDF.

## Error handling

- [ ] Uploading a non-SBOM file (e.g. a random `.json`) shows a readable error plus a
      recovery hint ("Make sure the file is an SBOM…").
- [ ] A truncated/corrupt SBOM shows the "corrupted or incomplete" hint.

## Uninstall

- [ ] Uninstalling via the documented path removes the app cleanly.

Sign-off: the audit is closed only after one full pass with every box checked on a real
Windows machine.
