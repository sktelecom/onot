// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { type NoticeSettings, SettingsPanel } from "./SettingsPanel";

const base: NoticeSettings = { formats: ["html"], lang: "en", company: {} };

describe("SettingsPanel", () => {
  it("toggles output formats", () => {
    const onChange = vi.fn();
    render(<SettingsPanel uiLang="en" value={base} onChange={onChange} />);
    fireEvent.click(screen.getByLabelText("pdf"));
    expect(onChange).toHaveBeenCalledWith({ ...base, formats: ["html", "pdf"] });
  });

  it("removes a checked format", () => {
    const onChange = vi.fn();
    render(<SettingsPanel uiLang="en" value={base} onChange={onChange} />);
    fireEvent.click(screen.getByLabelText("html"));
    expect(onChange).toHaveBeenCalledWith({ ...base, formats: [] });
  });

  it("updates company organization", () => {
    const onChange = vi.fn();
    render(<SettingsPanel uiLang="en" value={base} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Organization"), { target: { value: "SKT" } });
    expect(onChange).toHaveBeenCalledWith({ ...base, company: { organization: "SKT" } });
  });
});
