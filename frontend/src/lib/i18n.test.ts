// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from "vitest";
import { messages, t } from "./i18n";

describe("i18n", () => {
  it("no message is empty", () => {
    for (const value of Object.values(messages.en)) {
      expect(value.length).toBeGreaterThan(0);
    }
  });

  it("t returns localized strings", () => {
    expect(t("en", "title")).toBe("OSS Notice Generator");
  });
});
