// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OutputPanel } from "./OutputPanel";
import type { NoticeSettings } from "./SettingsPanel";

const base: NoticeSettings = { formats: ["html"], lang: "en", company: {}, remember: false };

function renderPanel(overrides: Partial<React.ComponentProps<typeof OutputPanel>> = {}) {
  const props = {
    uiLang: "en" as const,
    value: base,
    onChange: vi.fn(),
    onSave: vi.fn(),
    onPreview: vi.fn(),
    ready: true,
    saving: false,
    rendering: false,
    ...overrides,
  };
  render(<OutputPanel {...props} />);
  return props;
}

describe("OutputPanel", () => {
  it("toggles output formats", () => {
    const { onChange } = renderPanel();
    fireEvent.click(screen.getByLabelText("PDF"));
    expect(onChange).toHaveBeenCalledWith({ ...base, formats: ["html", "pdf"] });
  });

  it("removes a checked format", () => {
    const { onChange } = renderPanel();
    fireEvent.click(screen.getByLabelText("HTML"));
    expect(onChange).toHaveBeenCalledWith({ ...base, formats: [] });
  });

  it("names the format on the primary button when only one is selected", () => {
    renderPanel();
    expect(screen.getByTestId("save-notice")).toHaveTextContent("Save notice (HTML)");
  });

  it("counts the notices when several formats are selected", () => {
    renderPanel({ value: { ...base, formats: ["html", "pdf", "text"] } });
    expect(screen.getByTestId("save-notice")).toHaveTextContent("Save 3 notices");
  });

  it("saving is the primary action and preview the secondary one", () => {
    renderPanel();
    // The goal is a file on disk; the preview is a step on the way to it.
    expect(screen.getByTestId("save-notice")).toHaveClass("bg-brand");
    expect(screen.getByTestId("generate-preview")).not.toHaveClass("bg-brand");
  });

  it("disables both actions until an SBOM has been parsed", () => {
    renderPanel({ ready: false });
    expect(screen.getByTestId("save-notice")).toBeDisabled();
    expect(screen.getByTestId("generate-preview")).toBeDisabled();
    expect(screen.getByText(/upload an sbom file/i)).toBeInTheDocument();
  });

  it("explains why saving is unavailable with no format selected", () => {
    renderPanel({ value: { ...base, formats: [] } });
    expect(screen.getByTestId("save-notice")).toBeDisabled();
    expect(screen.getByText(/select at least one output format/i)).toBeInTheDocument();
  });

  it("marks the button busy while a save is in flight", () => {
    renderPanel({ saving: true });
    const button = screen.getByTestId("save-notice");
    expect(button).toHaveAttribute("aria-busy", "true");
    expect(button).toHaveTextContent("Saving...");
    expect(button).toBeDisabled();
  });
});
