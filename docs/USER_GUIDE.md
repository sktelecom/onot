# onot User Guide

This guide walks you through everything from downloading onot to saving a notice,
with screenshots. You don't need to install any developer tools, just one installer.

Everything runs on your own machine. Your SBOM file is never sent to any server, and
the app works without an internet connection.

## 1. Download

Go to the [Releases page](https://github.com/sktelecom/onot/releases) and take the
file for your system from the latest version at the top.

| System | File |
|--|--|
| Windows 10 or 11, 64-bit | `onot-Setup-x.y.z.exe` |
| macOS 12 or later | `onot-x.y.z.dmg` |

Linux is not published as a download. See the README if you want to build an AppImage
from source.

## 2. Install

The installers are not code-signed, so each system asks you to confirm the first
launch. This is the only extra step; there is nothing else to set up.

### Windows

Double-click `onot-Setup-x.y.z.exe`. SmartScreen may show "Windows protected your PC"
or an "unknown publisher" warning. Click **More info**, then the **Run anyway** button
that appears, and the installation continues. When it finishes, an onot icon is added
to the Start menu and the desktop.

### macOS

Open the `.dmg` and drag onot to Applications. On the first launch, right-click (or
Control-click) the app and choose **Open**, then confirm in the dialog. Double-clicking
instead of using **Open** gives a Gatekeeper warning with no way past it. You only need
to do this once.

## 3. Launch the app: first screen

When you start onot, the screen below appears. The screen is laid out in the three
steps you work through: the SBOM on the left, and the notice details and output
settings on the right. The app is in English.

![onot first screen](images/01-home.png)

On the first launch the app may spend up to a minute showing "Starting the local
engine". That is your antivirus scanning a freshly downloaded application. Later
launches are immediate.

The control in the top right switches between the light and dark themes. It follows
your system setting until you choose otherwise.

## 4. Add an SBOM file (step 1)

Drag an SBOM file onto the dashed area, or click the area to pick a file from the
chooser. You can also use **File > Open SBOM** in the menu. SPDX
(JSON/YAML/Tag-Value/RDF), CycloneDX (JSON/XML), and Excel formats are accepted. The
format is detected automatically, so you don't need to select it.

Don't have an SBOM file yet? Click **Try a sample** below the drop area to load a small
example that ships with the app, so you can see the whole flow right away.

Once the file is read, onot summarises it: the product name, how many components and
licenses it found, and how many components fall under each license. If anything needs
your attention, a warning count appears; open it to see what each warning means for the
notice you are about to produce.

![After adding an SBOM file](images/02-uploaded.png)

## 5. Fill in the notice details (step 2)

These fields are optional, and they appear in the generated notice: your organization,
a contact address for compliance questions, where the source code can be obtained, and
the copyright holder if it differs from the organization.

Tick **Remember these details** to keep them for next time. They are stored only on this
machine, and only when you tick the box.

## 6. Choose formats and save (step 3)

Choose the output formats you want. You can select several of HTML, Text, Markdown and
PDF.

![Choosing output formats](images/03-settings.png)

**Preview** shows the notice inside the app before you commit to a file. The component
list, licenses and copyright information are laid out in a table, and the full license
texts follow. Use **Expand** to give the preview the height of the window.

![Notice preview](images/04-preview.png)

**Save notice** writes the files. A "Save as" dialog opens for each format, and once a
file is written the app tells you where it went, with a **Show in folder** button. The
keyboard shortcut is Ctrl+S, or Cmd+S on macOS.

## Frequently asked questions

The installer warns about an unknown publisher, or my antivirus flagged it.
: The installers are not code-signed, and some antivirus tools flag a freshly built
  unsigned application by heuristic. On Windows choose **More info** then **Run anyway**;
  on macOS right-click the app and choose **Open**. If the file was quarantined, restore
  it from the quarantine (or add an exception) and run it again. The app runs entirely on
  your machine and makes no outbound network calls.

The app takes a while to start.
: The first launch waits for your antivirus to finish scanning the application, which can
  take up to a minute on Windows. The window shows "Starting the local engine" while it
  waits. Later launches are immediate.

What do I need to run it?
: A 64-bit Windows 10 or 11 PC, or a Mac on macOS 12 or later. Nothing else, no Python and
  no separate runtime. Everything the app needs is inside the one download.

How do I uninstall it?
: On Windows, open Settings then Apps then Installed apps, find onot, and choose
  **Uninstall**; the Start menu also has an onot uninstaller. On macOS, drag the app from
  Applications to the Trash.

Can I use it in an environment without internet?
: Yes. The full license texts are bundled with the app, so it works without a network.

Is my SBOM file sent anywhere?
: No. Parsing and notice generation all happen on your machine.

Can I use the command line (CLI) or build from source?
: Yes. See the CLI and developer sections in the [README](../README.md).
