// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// 사용자 가이드용 앱 화면 캡처 스크립트(일회성 문서 생성 도구).
// 실제 Electron 데스크톱 앱을 띄워 한국어 UI로 업로드→파싱→미리보기 흐름을 캡처한다.
// 실행: pnpm -C electron exec node scripts/capture-screenshots.mjs
// 산출물: docs/images/01~04-*.png. e2e 하니스와 동일한 _electron 런처를 쓰되 단언 없이 캡처만 한다.
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
  // 첫 창은 en UI로 뜬다. 렌더 완료를 기다린 뒤 한국어로 전환한다.
  await w.getByText("OSS Notice Generator").waitFor({ state: "visible", timeout: 60000 });
  await w.getByLabel("UI language").selectOption("ko");
  await w.waitForTimeout(400);
  await shot(w, "01-home.png");

  // SBOM 업로드 → 파싱 결과 카드(문서명/컴포넌트 수)가 뜰 때까지 대기.
  await w.getByTestId("file-input").setInputFiles(fixture);
  await w.getByText("example-product").waitFor({ state: "visible", timeout: 30000 });
  await w.waitForTimeout(400);
  await shot(w, "02-uploaded.png");

  // 출력 포맷을 하나 더 켜고(markdown) 고지문 언어를 한국어로 설정.
  const md = w.getByRole("checkbox", { name: "markdown", exact: true });
  if (!(await md.isChecked())) await md.check();
  await w.getByLabel("Notice language").selectOption("ko").catch(() => {});
  await w.waitForTimeout(300);
  await shot(w, "03-settings.png");

  // 미리보기 생성 → 미리보기 카드가 채워질 때까지 대기.
  await w.getByTestId("generate-preview").click();
  await w.waitForTimeout(2500);
  await shot(w, "04-preview.png");
} finally {
  await app.close();
}
console.log("captured: docs/images/01~04-*.png");
