// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Scenario 2: the PDF is produced via the Electron printToPDF path, not the sidecar (weasyprint).
// Save notice (PDF) → window.onot.exportPdf → ipcMain "export-pdf" → offscreen printToPDF → dialog → fs.writeFile.
// Stub dialog.showSaveDialog at runtime to inject the save path (no changes to production).
// (Notice content is verified server-side by pytest — here we only go as far as producing a valid PDF.)
import { expect, test } from "@playwright/test";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { launchApp, saveButton, setFormat, spdxFixture, uploadAndWaitParse } from "./_helpers.mjs";

test("exports a valid PDF via Electron printToPDF", async () => {
  test.setTimeout(90000); // Local offscreen rendering can be slow, so allow extra time.
  const { app, window } = await launchApp();
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), "onot-e2e-pdf-"));
  const pdfPath = path.join(dir, "OSS_Notice.pdf");
  try {
    await uploadAndWaitParse(window, spdxFixture);
    await setFormat(window, "pdf");

    // Stub showSaveDialog in the main process so it always returns a fixed path.
    await app.evaluate(async ({ dialog }, p) => {
      dialog.showSaveDialog = async () => ({ canceled: false, filePath: p });
    }, pdfPath);

    await saveButton(window).click();

    await waitForFile(pdfPath);
    const buf = await fs.readFile(pdfPath);
    expect(buf.subarray(0, 5).toString("latin1")).toBe("%PDF-");
    expect(buf.length).toBeGreaterThan(1000);
  } finally {
    await app.close();
    await fs.rm(dir, { recursive: true, force: true });
  }
});

async function waitForFile(p, timeoutMs = 30000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const st = await fs.stat(p);
      if (st.size > 0) return;
    } catch {
      // not there yet
    }
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error(`PDF not written: ${p}`);
}
