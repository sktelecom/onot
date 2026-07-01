// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Guards the packaged file:// render path (issue #68 / QA O-4). The other E2E specs load the
// frontend over http:// (dev server), where absolute asset paths happen to work, so they cannot
// catch a blank screen caused by file:// asset resolution. This launches the app in production
// loadFile mode against the built frontend/dist and asserts the UI actually mounts.
import { _electron as electron, expect, test } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const electronRoot = path.resolve(here, "..");
const frontendDist = path.resolve(here, "..", "..", "frontend", "dist");

test("packaged file:// load renders the UI (no blank screen)", async () => {
  const consoleErrors = [];
  const app = await electron.launch({
    args: [electronRoot],
    cwd: electronRoot,
    env: { ...process.env, ONOT_FRONTEND_DIR: frontendDist },
  });
  const window = await app.firstWindow();
  window.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  try {
    // If assets fail to load over file://, React never mounts and this text never appears.
    await expect(window.getByText("OSS Notice Generator")).toBeVisible({ timeout: 60000 });
    // Confirm we exercised the production path, not the dev server.
    expect(await window.evaluate(() => window.location.protocol)).toBe("file:");
    // The blank-screen signature was ERR_FILE_NOT_FOUND on the bundled assets.
    expect(consoleErrors.filter((e) => /ERR_FILE_NOT_FOUND/i.test(e))).toEqual([]);

    // The bundled sample must be usable over file:// (embedded in the JS bundle, not fetched):
    // a first-time user clicks "Try a sample" and the sidecar parses it end to end.
    await window.getByTestId("try-sample").click();
    await expect(window.getByText("example-product")).toBeVisible({ timeout: 30000 });
  } finally {
    await app.close();
  }
});
