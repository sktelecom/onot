// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Playwright-electron E2E 공통 헬퍼. testMatch(**/*.e2e.mjs)에 안 걸리므로 테스트로 수집되지 않고 import만 된다.
import { _electron as electron, expect } from "@playwright/test";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
export const electronRoot = path.resolve(here, "..");
export const repoRoot = path.resolve(here, "..", "..");
export const spdxFixture = path.join(repoRoot, "tests", "fixtures", "sbom", "example.spdx.json");

// 앱 기동 + 첫 창이 렌더될 때까지 대기. 기존 app.e2e.mjs와 동일 패턴.
export async function launchApp() {
  const app = await electron.launch({ args: [electronRoot], cwd: electronRoot });
  const window = await app.firstWindow();
  await expect(window.getByText("OSS Notice Generator")).toBeVisible({ timeout: 60000 });
  return { app, window };
}

// 창 URL 쿼리(?apiBase=)에서 사이드카 베이스 URL(http://127.0.0.1:<port>)을 추출한다.
export async function getApiBase(window) {
  const search = await window.evaluate(() => window.location.search);
  const apiBase = new URLSearchParams(search).get("apiBase");
  if (!apiBase) throw new Error(`apiBase not found in window URL search: ${search}`);
  return apiBase;
}

// 파일 업로드 후 파싱 성공 신호(문서명)가 보일 때까지 대기.
export async function uploadAndWaitParse(window, fixture, expectText = "example-product") {
  await window.getByTestId("file-input").setInputFiles(fixture);
  await expect(window.getByText(expectText)).toBeVisible({ timeout: 30000 });
}

// 출력 포맷 체크박스 토글(미체크면 체크). Download 버튼은 체크된 포맷만 렌더된다.
export async function setFormat(window, fmt) {
  const box = window.getByRole("checkbox", { name: fmt, exact: true });
  if (!(await box.isChecked())) await box.check();
}

// 고지문 언어 select. label 텍스트는 en UI 기준 "Notice language".
export async function setNoticeLang(window, lang) {
  await window.getByLabel("Notice language").selectOption(lang);
}

// sidecar.mjs의 ping과 동일 로직: 200이면 true, 그 외/에러/타임아웃이면 false.
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

// healthy()가 want와 같아질 때까지 폴링. 충족하면 true, 타임아웃이면 false.
export async function waitHealthy(apiBase, want, { timeoutMs = 10000, intervalMs = 250 } = {}) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if ((await healthy(apiBase)) === want) return true;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return false;
}
