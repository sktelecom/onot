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

// Extract the sidecar base URL (http://127.0.0.1:<port>) from the window URL query (?apiBase=).
export async function getApiBase(window) {
  const search = await window.evaluate(() => window.location.search);
  const apiBase = new URLSearchParams(search).get("apiBase");
  if (!apiBase) throw new Error(`apiBase not found in window URL search: ${search}`);
  return apiBase;
}

// After uploading a file, wait until the parse-success signal (the document name) becomes visible.
export async function uploadAndWaitParse(window, fixture, expectText = "example-product") {
  await window.getByTestId("file-input").setInputFiles(fixture);
  await expect(window.getByText(expectText)).toBeVisible({ timeout: 30000 });
}

// Toggle the output-format checkbox (check it if unchecked). The Download button is rendered only for checked formats.
export async function setFormat(window, fmt) {
  const box = window.getByRole("checkbox", { name: fmt, exact: true });
  if (!(await box.isChecked())) await box.check();
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
