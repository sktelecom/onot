// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// 시나리오 3: 잘못된 SBOM 업로드 시 실제 사이드카가 4xx를 반환하고,
// api.ts detail() → App setError → role="alert"로 이어지는 에러 UX 전체 체인이 동작하는지.
// (pytest는 400 응답만 검증 — 에러가 UI까지 표면화되는지는 통합에서만.)
// 디스크 fixture 없이 인메모리 buffer 업로드로 사이드카 IngestError(400)를 유발한다.
import { expect, test } from "@playwright/test";
import { launchApp } from "./_helpers.mjs";

test("surfaces an error alert when the sidecar rejects an invalid SBOM", async () => {
  const { app, window } = await launchApp();
  try {
    await window.getByTestId("file-input").setInputFiles({
      name: "x.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("not an sbom"),
    });

    const alert = window.getByRole("alert");
    await expect(alert).toBeVisible({ timeout: 30000 });
    await expect(alert).toContainText("Error");
    // negative 보강: 파싱이 성공하지 않았으므로 문서명 카드가 뜨면 안 된다.
    await expect(window.getByText("example-product")).toHaveCount(0);
  } finally {
    await app.close();
  }
});
