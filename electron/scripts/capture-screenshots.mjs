// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// App screenshot capture script for the user guide (one-off documentation tool).
// Launches the real Electron desktop app and captures the upload→parse→preview flow.
// Run: pnpm -C electron exec node scripts/capture-screenshots.mjs
// Output: docs/images/01~04-*.png. Uses the same _electron launcher as the e2e harness, but only captures without assertions.
import { _electron as electron } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const electronRoot = path.resolve(here, "..");
const repoRoot = path.resolve(here, "..", "..");
const fixture = path.join(repoRoot, "tests", "fixtures", "sbom", "example.spdx.json");
const outDir = path.join(repoRoot, "docs", "images");
fs.mkdirSync(outDir, { recursive: true });

const shot = (w, name) => w.screenshot({ path: path.join(outDir, name) });

const app = await electron.launch({ args: [electronRoot], cwd: electronRoot });
try {
  const w = await app.firstWindow();
  // Wait for the first window to finish rendering.
  await w.getByText("OSS Notice Generator").waitFor({ state: "visible", timeout: 60000 });
  await w.waitForTimeout(400);
  await shot(w, "01-home.png");

  // Upload SBOM → wait until the parse-result card (document name/component count) appears.
  await w.getByTestId("file-input").setInputFiles(fixture);
  await w.getByText("example-product").waitFor({ state: "visible", timeout: 30000 });
  await w.waitForTimeout(400);
  await shot(w, "02-uploaded.png");

  // Enable one more output format (markdown).
  const md = w.getByRole("checkbox", { name: "markdown", exact: true });
  if (!(await md.isChecked())) await md.check();
  await w.waitForTimeout(300);
  await shot(w, "03-settings.png");

  // Generate preview → wait until the preview card is filled.
  await w.getByTestId("generate-preview").click();
  await w.waitForTimeout(2500);
  await shot(w, "04-preview.png");
} finally {
  await app.close();
}
console.log("captured: docs/images/01~04-*.png");
