// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Scenario 4: on app shutdown, the sidecar is terminated along with it so no orphan process remains.
// main's sidecar pid is not exposed externally, so verify via healthz on the apiBase port.
// 200 after startup → app.close() → poll until the same port refuses connections (= process terminated).
// (node:test sidecar.test.mjs only does a manual spawn — whether the real app-shutdown hook kills the child is covered only in E2E.)
import { expect, test } from "@playwright/test";
import { getApiBase, healthy, launchApp, waitHealthy } from "./_helpers.mjs";

test("terminates the sidecar on app close (no orphan)", async () => {
  const { app, window } = await launchApp();
  const apiBase = await getApiBase(window);

  // Startup: the sidecar must be alive.
  expect(await waitHealthy(apiBase, true, { timeoutMs: 10000 })).toBe(true);

  await app.close();

  // Shutdown: allow for SIGTERM (up to 5s) → SIGKILL (2s) and poll until the port dies.
  expect(await waitHealthy(apiBase, false, { timeoutMs: 12000 })).toBe(true);
  expect(await healthy(apiBase)).toBe(false);
});
