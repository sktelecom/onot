// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FileDropzone } from "./FileDropzone";

describe("FileDropzone", () => {
  it("renders the prompt and labels the input", () => {
    render(<FileDropzone lang="en" onFile={() => {}} />);
    expect(screen.getByText(/drop an sbom file/i)).toBeInTheDocument();
    expect(screen.getByTestId("file-input")).toHaveAttribute("aria-label");
  });

  it("hints the OS chooser toward SBOM types via accept (U3)", () => {
    render(<FileDropzone lang="en" onFile={() => {}} />);
    const accept = screen.getByTestId("file-input").getAttribute("accept") ?? "";
    for (const ext of [".json", ".yaml", ".xml", ".spdx", ".xlsx"]) {
      expect(accept).toContain(ext);
    }
  });

  it("calls onFile when a file is selected", () => {
    const onFile = vi.fn();
    render(<FileDropzone lang="en" onFile={onFile} />);
    const input = screen.getByTestId("file-input") as HTMLInputElement;
    const file = new File(["x"], "a.spdx.json", { type: "application/json" });
    fireEvent.change(input, { target: { files: [file] } });
    expect(onFile).toHaveBeenCalledWith(file);
  });

  it("calls onFile on drop", () => {
    const onFile = vi.fn();
    render(<FileDropzone lang="en" onFile={onFile} />);
    const file = new File(["x"], "b.cdx.json");
    fireEvent.drop(screen.getByTestId("dropzone"), { dataTransfer: { files: [file] } });
    expect(onFile).toHaveBeenCalledWith(file);
  });

  it("shows the selected file name", () => {
    render(<FileDropzone lang="en" onFile={() => {}} fileName="chosen.xlsx" />);
    expect(screen.getByText("chosen.xlsx")).toBeInTheDocument();
  });
});
