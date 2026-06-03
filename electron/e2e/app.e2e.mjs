// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Playwright-electron E2E: 실제 앱을 기동해 풀 플로우와 사이드카 수명주기를 검증.
// 플랜 §8.2 시나리오(풀 플로우/사이드카/오프라인/대용량 등)의 핵심 경로. CI(Win/mac)에서 실행.
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

    // 업로드 → 파싱(사이드카 /api/parse 왕복)
    await window.getByTestId("file-input").setInputFiles(spdxFixture);
    await expect(window.getByText("example-product")).toBeVisible({ timeout: 30000 });

    // 미리보기 생성(사이드카 /api/render → iframe)
    await window.getByTestId("generate-preview").click();
    await expect(window.locator("iframe")).toBeVisible({ timeout: 30000 });
  } finally {
    await app.close();
  }
});
