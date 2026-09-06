// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import assert from "node:assert/strict";
import test from "node:test";
import { buildMenuTemplate, LINKS } from "../lib/menu-template.mjs";

const options = {
  isDev: false,
  isMac: false,
  openExternal() {},
  onOpenSbom() {},
  onSaveNotice() {},
  onAbout() {},
};

function labels(template) {
  return template.map((item) => item.label ?? item.role);
}

function findSubmenu(template, label) {
  return template.find((item) => (item.label ?? item.role) === label)?.submenu ?? [];
}

function flatLabels(submenu) {
  return submenu.map((item) => item.label ?? item.role).filter(Boolean);
}

test("a release build offers no reload and no developer tools", () => {
  const view = findSubmenu(buildMenuTemplate(options), "View");
  const roles = flatLabels(view);
  assert.equal(roles.includes("reload"), false);
  assert.equal(roles.includes("toggleDevTools"), false);
  // Zoom and full screen are for the user and stay.
  assert.equal(roles.includes("resetZoom"), true);
  assert.equal(roles.includes("togglefullscreen"), true);
});

test("a development build keeps the developer items", () => {
  const view = findSubmenu(buildMenuTemplate({ ...options, isDev: true }), "View");
  const roles = flatLabels(view);
  assert.equal(roles.includes("reload"), true);
  assert.equal(roles.includes("toggleDevTools"), true);
});

test("File offers the two actions the app is for, with accelerators", () => {
  const file = findSubmenu(buildMenuTemplate(options), "File");
  const open = file.find((item) => item.label === "Open SBOM...");
  const save = file.find((item) => item.label === "Save Notice");
  assert.equal(open.accelerator, "CmdOrCtrl+O");
  assert.equal(save.accelerator, "CmdOrCtrl+S");
});

test("Help points at the documentation the app used to offer no route to", () => {
  const help = findSubmenu(buildMenuTemplate(options), "help");
  assert.deepEqual(flatLabels(help).slice(0, 3), [
    "User Guide",
    "Release Notes",
    "Report an Issue",
  ]);
  assert.match(LINKS.userGuide, /USER_GUIDE\.md$/);
});

test("About sits in the app menu on macOS and under Help elsewhere", () => {
  const mac = buildMenuTemplate({ ...options, isMac: true });
  assert.equal(labels(mac)[0], "onot");
  assert.equal(flatLabels(findSubmenu(mac, "onot")).includes("About onot"), true);
  assert.equal(flatLabels(findSubmenu(mac, "help")).includes("About onot"), false);

  const other = buildMenuTemplate(options);
  assert.equal(flatLabels(findSubmenu(other, "help")).includes("About onot"), true);
});

test("the callbacks the app passes in are the ones wired to the items", () => {
  let opened = 0;
  const template = buildMenuTemplate({ ...options, onOpenSbom: () => (opened += 1) });
  findSubmenu(template, "File")
    .find((item) => item.label === "Open SBOM...")
    .click();
  assert.equal(opened, 1);
});
