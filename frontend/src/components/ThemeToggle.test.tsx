// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";
import { ThemeToggle } from "./ThemeToggle";

afterEach(() => {
  localStorage.clear();
  delete document.documentElement.dataset.theme;
});

describe("ThemeToggle", () => {
  it("starts on System and marks it as the pressed option", () => {
    render(<ThemeToggle lang="en" />);
    expect(screen.getByTestId("theme-system")).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("theme-dark")).toHaveAttribute("aria-pressed", "false");
  });

  it("applies and remembers an explicit choice", async () => {
    render(<ThemeToggle lang="en" />);
    await userEvent.click(screen.getByTestId("theme-dark"));

    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(localStorage.getItem("onot.theme")).toBe("dark");
    expect(screen.getByTestId("theme-dark")).toHaveAttribute("aria-pressed", "true");
  });

  it("hands control back to the OS when System is chosen again", async () => {
    render(<ThemeToggle lang="en" />);
    await userEvent.click(screen.getByTestId("theme-light"));
    await userEvent.click(screen.getByTestId("theme-system"));

    expect(document.documentElement.dataset.theme).toBeUndefined();
    expect(localStorage.getItem("onot.theme")).toBe("system");
  });

  it("restores the stored preference on mount", () => {
    localStorage.setItem("onot.theme", "light");
    render(<ThemeToggle lang="en" />);
    expect(screen.getByTestId("theme-light")).toHaveAttribute("aria-pressed", "true");
  });
});
