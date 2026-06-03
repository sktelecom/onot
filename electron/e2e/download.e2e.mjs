// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// 시나리오 1: html/text/markdown 다운로드가 실제 파일시스템까지 도달하는지.
// 렌더러의 <a download> → Electron will-download → setSavePath로 tmp에 저장한 뒤 내용 단언.
// (HTTP 응답 바이트 자체는 pytest가 검증하므로, 여기서는 "실제 저장"이라는 통합 경로만 본다.)
import { expect, test } from "@playwright/test";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { launchApp, setFormat, spdxFixture, uploadAndWaitParse } from "./_helpers.mjs";

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
      // will-download를 가로채 tmp에 저장(프로덕션 코드 무수정). win에서도 Electron이 "/"를 처리한다.
      await app.evaluate(({ session }, saveDir) => {
        session.defaultSession.on("will-download", (_e, item) => {
          item.setSavePath(`${saveDir}/${item.getFilename()}`);
        });
      }, dir);

      await uploadAndWaitParse(window, spdxFixture);
      await setFormat(window, fmt);
      await window.getByRole("button", { name: new RegExp(`download ${fmt}`, "i") }).click();

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

// dir에 완성된(진행 중 .crdownload가 아닌, 크기>0) 파일이 나타날 때까지 폴링.
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
