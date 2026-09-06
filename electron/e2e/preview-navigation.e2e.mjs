// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// The notice's own navigation has to work inside the preview, and getting there took four
// things lining up: a blob: URL rather than srcdoc (an about:srcdoc document takes its base URL
// from the parent, so "#licenses" navigated the frame to the app and blanked the preview),
// blob: in the CSP frame-src, allow-same-origin on the sandbox (a fully opaque origin refuses
// its own anchor links), and a will-navigate rule that lets a subframe move within a blob URL.
// Any one of those regressing leaves a table of contents that looks fine and does nothing, so
// this asserts the outcome rather than any single mechanism.
import { expect, test } from "@playwright/test";
import { launchApp, spdxFixture, uploadAndWaitParse } from "./_helpers.mjs";

async function openPreview(window) {
  await uploadAndWaitParse(window, spdxFixture);
  await window.getByTestId("generate-preview").click();
  await expect(window.locator("iframe")).toBeVisible({ timeout: 30000 });
  return window.frameLocator("iframe");
}

function positions(frame) {
  return frame.locator("html").evaluate((el) => {
    const doc = el.ownerDocument;
    const top = (id) => Math.round(doc.getElementById(id)?.getBoundingClientRect().top ?? NaN);
    return {
      scrollTop: Math.round(doc.scrollingElement.scrollTop),
      headings: doc.querySelectorAll("h2").length,
      viewport: Math.round(doc.scrollingElement.clientHeight),
      licenses: top("licenses"),
      offer: top("offer"),
    };
  });
}

test("the contents links move the preview, and leave it intact", async () => {
  const { app, window } = await launchApp();
  try {
    const frame = await openPreview(window);
    const before = await positions(frame);
    expect(before.scrollTop).toBe(0);
    expect(before.headings).toBeGreaterThan(0);

    // In view, rather than pinned to the very top: the last section cannot reach the top
    // because there is not enough document below it to scroll past.
    const inView = async (key) => {
      const at = await positions(frame);
      return at[key] >= 0 && at[key] < at.viewport;
    };

    await frame.locator('nav.toc a[href="#licenses"]').click();
    await expect.poll(() => inView("licenses"), { timeout: 5000 }).toBe(true);

    await frame.locator('nav.toc a[href="#offer"]').click();
    await expect.poll(() => inView("offer"), { timeout: 5000 }).toBe(true);
    expect((await positions(frame)).scrollTop).toBeGreaterThan(before.scrollTop);

    // Still the notice, not the app: srcdoc used to navigate the frame away entirely.
    const after = await positions(frame);
    expect(after.headings).toBe(before.headings);
  } finally {
    await app.close();
  }
});

test("a licence links back to the component that uses it", async () => {
  const { app, window } = await launchApp();
  try {
    const frame = await openPreview(window);
    const href = await frame.locator(".license .used-by a").first().getAttribute("href");
    expect(href).toMatch(/^#pkg-/);

    await frame.locator(".license .used-by a").first().click();
    await expect
      .poll(
        () =>
          frame
            .locator("html")
            .evaluate(
              (el, id) =>
                Math.round(el.ownerDocument.getElementById(id).getBoundingClientRect().top),
              href.slice(1),
            ),
        { timeout: 5000 },
      )
      .toBeLessThanOrEqual(1);
  } finally {
    await app.close();
  }
});

test("the notice cannot run script in the preview", async () => {
  const { app, window } = await launchApp();
  try {
    await openPreview(window);
    const sandbox = await window.locator("iframe").getAttribute("sandbox");
    // allow-same-origin is needed for the anchors; allow-scripts must never join it, because
    // together they let a frame lift its own sandbox.
    expect(sandbox).toBe("allow-same-origin");
  } finally {
    await app.close();
  }
});
