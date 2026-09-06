// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// The menu as data. Kept free of any electron import so it can be built and asserted on under
// plain node; menu.mjs is the thin part that hands it to Electron.

const REPO = "https://github.com/sktelecom/onot";
export const LINKS = {
  userGuide: `${REPO}/blob/main/docs/USER_GUIDE.md`,
  issues: `${REPO}/issues/new`,
  // The newest release, for comparing against the version in About.
  latestRelease: `${REPO}/releases/latest`,
  changelog: `${REPO}/blob/main/CHANGELOG.md`,
};

/**
 * @param {object} options
 * @param {boolean} options.isDev        Developer items appear only in a development run.
 * @param {boolean} options.isMac
 * @param {(url: string) => void} options.openExternal
 * @param {() => void} options.onOpenSbom
 * @param {() => void} options.onSaveNotice
 * @param {() => void} options.onAbout
 */
export function buildMenuTemplate({
  isDev,
  isMac,
  openExternal = () => {},
  onOpenSbom,
  onSaveNotice,
  onAbout,
}) {
  const about = { label: "About onot", click: onAbout };
  const help = {
    role: "help",
    submenu: [
      { label: "User Guide", click: () => openExternal(LINKS.userGuide) },
      { label: "Release Notes", click: () => openExternal(LINKS.changelog) },
      { type: "separator" },
      // Opens the releases page in a browser rather than querying an API. onot's promise is
      // that it works offline and reaches nothing on its own, and a version check is not
      // worth spending that; About names the version installed, for comparison.
      { label: "Check for Updates...", click: () => openExternal(LINKS.latestRelease) },
      { label: "Report an Issue", click: () => openExternal(LINKS.issues) },
      ...(isMac ? [] : [{ type: "separator" }, about]),
    ],
  };

  return [
    ...(isMac
      ? [
          {
            label: "onot",
            submenu: [
              about,
              { type: "separator" },
              { role: "services" },
              { type: "separator" },
              { role: "hide" },
              { role: "hideOthers" },
              { role: "unhide" },
              { type: "separator" },
              { role: "quit" },
            ],
          },
        ]
      : []),
    {
      label: "File",
      submenu: [
        { label: "Open SBOM...", accelerator: "CmdOrCtrl+O", click: onOpenSbom },
        { label: "Save Notice", accelerator: "CmdOrCtrl+S", click: onSaveNotice },
        { type: "separator" },
        isMac ? { role: "close" } : { role: "quit" },
      ],
    },
    { role: "editMenu" },
    {
      label: "View",
      submenu: [
        { role: "resetZoom" },
        { role: "zoomIn" },
        { role: "zoomOut" },
        { type: "separator" },
        { role: "togglefullscreen" },
        // Reload and the developer tools are for us, not for someone generating a notice.
        ...(isDev ? [{ type: "separator" }, { role: "reload" }, { role: "toggleDevTools" }] : []),
      ],
    },
    { role: "windowMenu" },
    help,
  ];
}
