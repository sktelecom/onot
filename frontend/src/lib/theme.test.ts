// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { afterEach, describe, expect, it, vi } from "vitest";
import { applyTheme, initTheme, readPref, writePref } from "./theme";

afterEach(() => {
  localStorage.clear();
  delete document.documentElement.dataset.theme;
  vi.restoreAllMocks();
});

describe("theme", () => {
  it("defaults to following the system", () => {
    expect(readPref()).toBe("system");
  });

  it("ignores a stored value that is not a known preference", () => {
    localStorage.setItem("onot.theme", "solarized");
    expect(readPref()).toBe("system");
  });

  it("round-trips an explicit preference", () => {
    writePref("dark");
    expect(readPref()).toBe("dark");
  });

  it("leaves data-theme unset for 'system' so the stylesheet follows the OS", () => {
    applyTheme("dark");
    applyTheme("system");
    expect(document.documentElement.dataset.theme).toBeUndefined();
  });

  it("pins data-theme for an explicit choice", () => {
    applyTheme("light");
    expect(document.documentElement.dataset.theme).toBe("light");
  });

  it("applies the stored override at startup", () => {
    localStorage.setItem("onot.theme", "dark");
    initTheme();
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("still works when storage throws (private mode)", () => {
    vi.spyOn(localStorage, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    vi.spyOn(localStorage, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(readPref()).toBe("system");
    expect(() => writePref("dark")).not.toThrow();
  });
});
