// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Playwright-electron E2E: launch the real app to verify the full flow and the sidecar lifecycle.
// Core path of the plan §8.2 scenarios (full flow/sidecar/offline/large input, etc.). Runs in CI (Win/mac).
import { _electron as electron, expect, test } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const electronRoot = path.resolve(here, "..");
const repoRoot = path.resolve(here, "..", "..");
const spdxFixture = path.join(repoRoot, "tests", "fixtures", "sbom", "example.spdx.json");

test("launches, sidecar serves, full upload→parse→preview flow", async () => {
  const app = await electron.launch({ args: [electronRoot], cwd: electronRoot });
  try {
    const window = await app.firstWindow();
    await expect(window.getByText("OSS Notice Generator")).toBeVisible({ timeout: 60000 });

    // Upload → parse (round trip to the sidecar /api/parse)
    await window.getByTestId("file-input").setInputFiles(spdxFixture);
    await expect(window.getByText("example-product")).toBeVisible({ timeout: 30000 });

    // Generate preview (sidecar /api/render → iframe)
    await window.getByTestId("generate-preview").click();
    await expect(window.locator("iframe")).toBeVisible({ timeout: 30000 });
  } finally {
    await app.close();
  }
});
