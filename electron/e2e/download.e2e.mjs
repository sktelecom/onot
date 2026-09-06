// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Scenario 1: verify that html/text/markdown downloads reach the actual filesystem.
// Renderer's <a download> → Electron will-download → setSavePath saves to tmp, then assert the content.
// (The HTTP response bytes themselves are verified by pytest, so here we only check the "actual save" integration path.)
import { expect, test } from "@playwright/test";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { launchApp, saveButton, setFormat, spdxFixture, uploadAndWaitParse } from "./_helpers.mjs";

const CASES = [
  { fmt: "html", contains: "OSS Notice for example-product" },
  { fmt: "text", contains: "example-product" },
  { fmt: "markdown", contains: "example-product" },
];

for (const { fmt, contains } of CASES) {
  test(`downloads ${fmt} to disk via will-download`, async () => {
    const { app, window } = await launchApp();
    const dir = await fs.mkdtemp(path.join(os.tmpdir(), "onot-e2e-dl-"));
    try {
      // Intercept will-download and save to tmp (no changes to production code). Electron handles "/" on win too.
      await app.evaluate(({ session }, saveDir) => {
        session.defaultSession.on("will-download", (_e, item) => {
          item.setSavePath(`${saveDir}/${item.getFilename()}`);
        });
      }, dir);

      await uploadAndWaitParse(window, spdxFixture);
      await setFormat(window, fmt);
      await saveButton(window).click();

      const saved = await waitForDownloadedFile(dir);
      const body = await fs.readFile(saved, "utf8");
      expect(body.length).toBeGreaterThan(0);
      expect(body).toContain(contains);
    } finally {
      await app.close();
      await fs.rm(dir, { recursive: true, force: true });
    }
  });
}

// Poll until a completed file (not an in-progress .crdownload, size > 0) appears in dir.
async function waitForDownloadedFile(dir, timeoutMs = 15000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const files = (await fs.readdir(dir)).filter((f) => !f.endsWith(".crdownload"));
    for (const f of files) {
      const full = path.join(dir, f);
      const st = await fs.stat(full);
      if (st.size > 0) return full;
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error(`no completed download appeared in ${dir}`);
}
