// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { describe, expect, it } from "vitest";
import { messages, t } from "./i18n";

describe("i18n", () => {
  it("en and ko have identical key sets", () => {
    expect(Object.keys(messages.en).sort()).toEqual(Object.keys(messages.ko).sort());
  });

  it("no message is empty", () => {
    for (const lang of ["en", "ko"] as const) {
      for (const value of Object.values(messages[lang])) {
        expect(value.length).toBeGreaterThan(0);
      }
    }
  });

  it("t returns localized strings", () => {
    expect(t("en", "title")).toBe("OSS Notice Generator");
    expect(t("ko", "title")).toBe("오픈소스 고지문 생성기");
  });
});
