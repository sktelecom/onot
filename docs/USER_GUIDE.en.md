# onot User Guide (Windows)

> 한국어 안내는 [USER_GUIDE.md](USER_GUIDE.md)를 참고하세요.

This guide walks you through everything from downloading onot to saving a notice,
with screenshots. You don't need to install any developer tools — just one installer.

Everything runs on your own PC. Your SBOM file is never sent to any server, and the
app works without an internet connection.

## 1. Download the installer

Go to the [Releases page](https://github.com/sktelecom/onot/releases). From the
latest version at the top, download `onot-Setup-x.y.z.exe` (`x.y.z` is the version
number).

## 2. Install

Double-click the downloaded `onot-Setup-x.y.z.exe` to run it.

Because the installer is not code-signed, Windows SmartScreen may show a
"Windows protected your PC" or "unknown publisher" warning on first run. Click
**More info** in the dialog, then the **Run anyway** button that appears, and the
installation continues. When it finishes, an onot icon is added to the Start menu
and desktop.

## 3. Launch the app: first screen

When you start onot, the screen below appears. Use the `KO`/`EN` switch in the top
right to change the interface language. The dashed area on the left is where you drop
your SBOM file; the right side holds the output settings.

![onot first screen](images/01-home.png)

## 4. Upload an SBOM file

Drag an SBOM file onto the dashed area, or click the area to pick a file from the
chooser. SPDX (JSON/YAML/Tag-Value/RDF), CycloneDX (JSON/XML), and Excel formats are
accepted. The format is detected automatically, so you don't need to select it.

Once uploaded, the document name and component count are shown. In the screenshot
below, `example.spdx.json` was uploaded and 2 components of `EXAMPLE-PRODUCT` were
recognized.

![After uploading an SBOM file](images/02-uploaded.png)

## 5. Choose output formats and details

On the right, choose the output formats you want (you can select several of html,
text, markdown, pdf). Set the notice language to Korean or English, and optionally
enter your organization name, contact email, and source code URL. This information is
included in the generated notice.

After you pick formats, a download button appears for each one below. In the
screenshot below, html and markdown were both selected, so two download buttons
appeared.

![Choosing output formats](images/03-settings.png)

## 6. Preview and download

Click **Generate preview** to view the notice right inside the app. The component
list, licenses, and copyright information are laid out in a table, and the full
license texts are included as well.

![Notice preview](images/04-preview.png)

Once you've reviewed it, click the button for the format you want — such as
**Download html** or **Download markdown** — to save the file. For PDF, a dialog asks
where to save.

## Frequently asked questions

A SmartScreen warning appears during installation.
: This happens because the installer is not code-signed. Click **More info**, then
  **Run anyway** to install.

Can I use it in an environment without internet?
: Yes. The full license texts are bundled with the app, so it works without a network.

Is my SBOM file sent anywhere?
: No. Parsing and notice generation all happen on your PC.

Can I use the command line (CLI) or build from source?
: Yes. See the CLI and developer sections in the [README](../README.md).
