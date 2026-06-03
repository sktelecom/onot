// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// 시나리오 4: 앱 종료 시 사이드카가 동반 종료되어 고아 프로세스가 남지 않는지.
// main의 sidecar pid는 외부로 노출되지 않으므로, apiBase 포트의 healthz로 검증한다.
// 기동 후 200 → app.close() → 같은 포트가 연결 거부될 때까지(=프로세스 종료) 폴링.
// (node:test sidecar.test.mjs는 수동 spawn만 — 실제 앱 종료 훅이 자식을 죽이는지는 E2E에서만.)
import { expect, test } from "@playwright/test";
import { getApiBase, healthy, launchApp, waitHealthy } from "./_helpers.mjs";

test("terminates the sidecar on app close (no orphan)", async () => {
  const { app, window } = await launchApp();
  const apiBase = await getApiBase(window);

  // 기동: 사이드카가 살아있어야 한다.
  expect(await waitHealthy(apiBase, true, { timeoutMs: 10000 })).toBe(true);

  await app.close();

  // 종료: SIGTERM(최대 5s) → SIGKILL(2s) 여유를 두고 포트가 죽는지 폴링.
  expect(await waitHealthy(apiBase, false, { timeoutMs: 12000 })).toBe(true);
  expect(await healthy(apiBase)).toBe(false);
});
