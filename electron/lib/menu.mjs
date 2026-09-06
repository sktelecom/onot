// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Application menu. Without one, Electron installs its default, which offers end users Reload
// and Toggle Developer Tools while offering no About and no way to reach the documentation.
// The template itself lives in menu-template.mjs, which imports nothing from electron.
import { Menu, shell } from "electron";
import { buildMenuTemplate } from "./menu-template.mjs";

export function installMenu(options) {
  const template = buildMenuTemplate({
    ...options,
    openExternal: (url) => shell.openExternal(url),
  });
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}
