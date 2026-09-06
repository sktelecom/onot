// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Shared helpers for Playwright-electron E2E. Not matched by testMatch(**/*.e2e.mjs), so it is only imported and never collected as a test.
import { _electron as electron, expect } from "@playwright/test";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
export const electronRoot = path.resolve(here, "..");
export const repoRoot = path.resolve(here, "..", "..");
export const spdxFixture = path.join(repoRoot, "tests", "fixtures", "sbom", "example.spdx.json");

// Launch the app and wait until the first window has rendered. Same pattern as the existing app.e2e.mjs.
export async function launchApp() {
  const app = await electron.launch({ args: [electronRoot], cwd: electronRoot });
  const window = await app.firstWindow();
  await expect(window.getByText("OSS Notice Generator")).toBeVisible({ timeout: 60000 });
  return { app, window };
}

// The sidecar base URL (http://127.0.0.1:<port>). The window is created before the sidecar has
// a port, so it is no longer in the URL; the preload bridge answers once the port exists.
export async function getApiBase(window) {
  const apiBase = await window.evaluate(() => window.onot.getApiBase());
  if (!apiBase) throw new Error("the bridge returned no apiBase");
  return apiBase;
}

// After uploading a file, wait until the parse-success signal (the document name) becomes visible.
export async function uploadAndWaitParse(window, fixture, expectText = "example-product") {
  await window.getByTestId("file-input").setInputFiles(fixture);
  await expect(window.getByText(expectText)).toBeVisible({ timeout: 30000 });
}

// Output formats are labelled the way a reader spells them, not by their API identifier.
const FORMAT_LABELS = { html: "HTML", text: "Text", markdown: "Markdown", pdf: "PDF" };

// Check the given format, and uncheck every other one so a save produces exactly this file.
export async function setFormat(window, fmt) {
  for (const [id, label] of Object.entries(FORMAT_LABELS)) {
    const box = window.getByRole("checkbox", { name: label, exact: true });
    if ((await box.isChecked()) !== (id === fmt)) await box.setChecked(id === fmt);
  }
}

// The primary action. Its label names the format, so match on the test id instead.
export function saveButton(window) {
  return window.getByTestId("save-notice");
}

// Same logic as ping in sidecar.mjs: true on 200, false otherwise/on error/on timeout.
export function healthy(apiBase) {
  return new Promise((resolve) => {
    const req = http.get(`${apiBase}/healthz`, { timeout: 1000 }, (res) => {
      res.resume();
      resolve(res.statusCode === 200);
    });
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

// Poll until healthy() equals want. Returns true when satisfied, false on timeout.
export async function waitHealthy(apiBase, want, { timeoutMs = 10000, intervalMs = 250 } = {}) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if ((await healthy(apiBase)) === want) return true;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return false;
}
