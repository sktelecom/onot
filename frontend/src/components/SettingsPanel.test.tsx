// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { type NoticeSettings, SettingsPanel } from "./SettingsPanel";

const base: NoticeSettings = { formats: ["html"], lang: "en", company: {}, remember: false };

describe("SettingsPanel", () => {
  it("updates company organization", () => {
    const onChange = vi.fn();
    render(<SettingsPanel uiLang="en" value={base} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Organization"), { target: { value: "SKT" } });
    expect(onChange).toHaveBeenCalledWith({ ...base, company: { organization: "SKT" } });
  });

  it("exposes the copyright holder, which the API accepted but the screen did not offer", () => {
    const onChange = vi.fn();
    render(<SettingsPanel uiLang="en" value={base} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Copyright holder"), { target: { value: "Acme" } });
    expect(onChange).toHaveBeenCalledWith({ ...base, company: { copyright_holder: "Acme" } });
  });

  it("uses input types that match the field, so the OS keyboard and validation fit", () => {
    render(<SettingsPanel uiLang="en" value={base} onChange={() => {}} />);
    expect(screen.getByLabelText("Contact email")).toHaveAttribute("type", "email");
    expect(screen.getByLabelText("Source code URL")).toHaveAttribute("type", "url");
  });

  it("keeps the details opt-in", () => {
    const onChange = vi.fn();
    render(<SettingsPanel uiLang="en" value={base} onChange={onChange} />);
    fireEvent.click(screen.getByLabelText("Remember these details"));
    expect(onChange).toHaveBeenCalledWith({ ...base, remember: true });
  });
});
