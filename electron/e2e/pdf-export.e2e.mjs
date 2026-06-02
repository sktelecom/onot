// 시나리오 2: PDF는 사이드카(weasyprint)가 아니라 Electron printToPDF 경로로 생성된다.
// Download pdf → window.onot.exportPdf → ipcMain "export-pdf" → offscreen printToPDF → dialog → fs.writeFile.
// dialog.showSaveDialog를 런타임 stub해 저장 경로를 주입한다(프로덕션 무수정).
// 한글(lang=ko) 고지문으로 생성해 CJK 입력에서도 PDF가 정상 산출되는지 본다.
// (한글 텍스트 강검증은 pytest test_render_lang_ko가 담당 — 여기서는 유효한 PDF 산출까지.)
import { expect, test } from "@playwright/test";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { launchApp, setFormat, setNoticeLang, spdxFixture, uploadAndWaitParse } from "./_helpers.mjs";

test("exports a valid PDF via Electron printToPDF (ko notice)", async () => {
  test.setTimeout(90000); // 로컬 offscreen 렌더가 느릴 수 있어 여유를 둔다.
  const { app, window } = await launchApp();
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), "onot-e2e-pdf-"));
  const pdfPath = path.join(dir, "OSS_Notice.pdf");
  try {
    await uploadAndWaitParse(window, spdxFixture);
    await setNoticeLang(window, "ko");
    await setFormat(window, "pdf");

    // showSaveDialog가 항상 고정 경로를 반환하도록 main 프로세스에서 stub.
    await app.evaluate(async ({ dialog }, p) => {
      dialog.showSaveDialog = async () => ({ canceled: false, filePath: p });
    }, pdfPath);

    await window.getByRole("button", { name: /download pdf/i }).click();

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
      // 아직 없음
    }
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error(`PDF not written: ${p}`);
}
