// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Scenario 3: on an invalid SBOM upload, the real sidecar returns a 4xx and
// the whole error-UX chain api.ts detail() → App setError → role="alert" works.
// (pytest only verifies the 400 response — whether the error surfaces all the way to the UI is covered only in integration.)
// Trigger a sidecar IngestError(400) via an in-memory buffer upload without a disk fixture.
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
    // Negative reinforcement: since parsing did not succeed, the document-name card must not appear.
    await expect(window.getByText("example-product")).toHaveCount(0);
  } finally {
    await app.close();
  }
});
