import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import * as api from "./lib/api";
import type { ParseResult } from "./lib/api";

vi.mock("./lib/api");
const parseSbom = vi.mocked(api.parseSbom);
const renderNotice = vi.mocked(api.renderNotice);

beforeEach(() => vi.resetAllMocks());
afterEach(() => {
  vi.restoreAllMocks();
  delete (window as Window & { onot?: unknown }).onot;
});

function parsed(name: string, count: number, warnings: string[] = []): ParseResult {
  return {
    document: {
      name,
      packages: Array.from({ length: count }, (_, i) => ({
        name: `p${i}`,
        version: "1",
        license_concluded: null,
        license_declared: null,
        copyright: null,
      })),
      licenses: [],
    },
    warnings,
  };
}

describe("App", () => {
  it("renders the title and has no a11y violations", async () => {
    const { container } = render(<App />);
    expect(screen.getByText("OSS Notice Generator")).toBeInTheDocument();
    // color-contrast is unreliable in jsdom, which has no real rendered colors/canvas.
    // Without disabling this rule, the unimplemented getContext makes it "incomplete" and silently skipped.
    // Contrast verification is delegated to the Playwright-electron E2E, which runs in a real browser.
    const results = await axe.run(container, {
      rules: { "color-contrast": { enabled: false } },
    });
    expect(results.violations).toEqual([]);
  });

  it("parses an uploaded file and shows package count", async () => {
    parseSbom.mockResolvedValue(parsed("demo-product", 2));
    render(<App />);
    await userEvent.upload(
      screen.getByTestId("file-input"),
      new File(["x"], "demo.spdx.json"),
    );
    await waitFor(() => expect(screen.getByText("demo-product")).toBeInTheDocument());
    expect(screen.getByText(/2 components/)).toBeInTheDocument();
  });

  it("shows warnings from parse", async () => {
    parseSbom.mockResolvedValue(parsed("p", 1, ["unknown license: Foo"]));
    render(<App />);
    await userEvent.upload(screen.getByTestId("file-input"), new File(["x"], "x.json"));
    await waitFor(() => expect(screen.getByText("unknown license: Foo")).toBeInTheDocument());
  });

  it("shows an error alert when parsing fails", async () => {
    parseSbom.mockRejectedValue(new Error("bad sbom"));
    render(<App />);
    await userEvent.upload(screen.getByTestId("file-input"), new File(["x"], "x.json"));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("bad sbom"));
  });

  it("keeps action buttons disabled after a parse failure (no repeat errors)", async () => {
    parseSbom.mockRejectedValue(new Error("bad sbom"));
    render(<App />);
    await userEvent.upload(screen.getByTestId("file-input"), new File(["x"], "x.json"));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("bad sbom"));
    // parsed === null after failure, so Generate/Download must stay disabled.
    expect(screen.getByTestId("generate-preview")).toBeDisabled();
    for (const btn of screen.getAllByRole("button", { name: /download/i })) {
      expect(btn).toBeDisabled();
    }
  });

  it("downloads with the backend-provided filename and revokes the object URL", async () => {
    parseSbom.mockResolvedValue(parsed("demo", 1));
    renderNotice.mockResolvedValue({ blob: new Blob(["x"]), filename: "OSS_Notice_demo.html" });
    const createUrl = vi.fn(() => "blob:mock");
    const revokeUrl = vi.fn();
    // jsdom lacks createObjectURL/revokeObjectURL, so define them directly
    Object.defineProperty(URL, "createObjectURL", { value: createUrl, configurable: true });
    Object.defineProperty(URL, "revokeObjectURL", { value: revokeUrl, configurable: true });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    let anchor: HTMLAnchorElement | undefined;
    const origCreate = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tag: string) => {
      const el = origCreate(tag);
      if (tag === "a") anchor = el as HTMLAnchorElement;
      return el;
    });

    render(<App />);
    await userEvent.upload(screen.getByTestId("file-input"), new File(["x"], "demo.spdx.json"));
    await waitFor(() => screen.getByText("demo"));
    await userEvent.click(screen.getByRole("button", { name: /download html/i }));

    await waitFor(() => expect(createUrl).toHaveBeenCalled());
    expect(anchor?.download).toBe("OSS_Notice_demo.html");
    expect(renderNotice).toHaveBeenCalledWith(
      expect.any(File),
      expect.objectContaining({ format: "html", download: true }),
    );
    await waitFor(() => expect(revokeUrl).toHaveBeenCalledWith("blob:mock"));
  });

  it("uses the Electron printToPDF bridge for pdf when available", async () => {
    parseSbom.mockResolvedValue(parsed("demo", 1));
    // jsdom does not support Blob.text() -> replace with a blob-like object that provides text()
    const blob = { text: async () => "<html>notice</html>" } as unknown as Blob;
    renderNotice.mockResolvedValue({ blob, filename: "x.html" });
    const exportPdf = vi.fn().mockResolvedValue({ saved: true });
    (window as Window & { onot?: unknown }).onot = { exportPdf };

    render(<App />);
    await userEvent.upload(screen.getByTestId("file-input"), new File(["x"], "demo.spdx.json"));
    await waitFor(() => screen.getByText("demo"));
    await userEvent.click(screen.getByLabelText("pdf")); // add pdf format in settings
    await userEvent.click(screen.getByRole("button", { name: /download pdf/i }));

    await waitFor(() => expect(exportPdf).toHaveBeenCalled());
    // renders HTML and hands it to printToPDF, not a sidecar PDF
    expect(renderNotice).toHaveBeenCalledWith(
      expect.any(File),
      expect.objectContaining({ format: "html" }),
    );
  });
});
