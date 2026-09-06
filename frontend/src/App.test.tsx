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

beforeEach(() => {
  vi.resetAllMocks();
  // The window opens before the sidecar is listening; every test here starts from "ready".
  vi.mocked(api.waitForApi).mockResolvedValue("");
});
afterEach(() => {
  vi.restoreAllMocks();
  delete (window as Window & { onot?: unknown }).onot;
  localStorage.clear();
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

async function upload(name = "demo.spdx.json") {
  await userEvent.upload(screen.getByTestId("file-input"), new File(["x"], name));
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

  it("says the engine is starting, and stops saying so once it is up", async () => {
    let ready: (base: string) => void = () => {};
    vi.mocked(api.waitForApi).mockReturnValue(
      new Promise<string>((resolve) => {
        ready = resolve;
      }),
    );
    render(<App />);
    expect(screen.getByTestId("engine-starting")).toBeInTheDocument();

    ready("");
    await waitFor(() => expect(screen.queryByTestId("engine-starting")).not.toBeInTheDocument());
  });

  it("parses an uploaded file and summarises it", async () => {
    parseSbom.mockResolvedValue(parsed("demo-product", 2));
    render(<App />);
    await upload();
    await waitFor(() => expect(screen.getByText("demo-product")).toBeInTheDocument());
    expect(screen.getByText(/2 components, 0 licenses/)).toBeInTheDocument();
  });

  it("keeps warnings collapsed until asked, with an explanation of each", async () => {
    parseSbom.mockResolvedValue(parsed("p", 1, ["no license information for foo 1.2.3"]));
    render(<App />);
    await upload();
    await waitFor(() => expect(screen.getByTestId("toggle-warnings")).toBeInTheDocument());
    expect(screen.getByTestId("toggle-warnings")).toHaveTextContent("1 warning");
    expect(screen.queryByText(/no license information for foo/)).not.toBeInTheDocument();

    await userEvent.click(screen.getByTestId("toggle-warnings"));
    expect(screen.getByText("no license information for foo 1.2.3")).toBeInTheDocument();
    expect(screen.getByText(/the notice lists this component without a license/i)).toBeInTheDocument();
  });

  it("shows an error alert when parsing fails, and lets it be dismissed", async () => {
    parseSbom.mockRejectedValue(new Error("bad sbom"));
    render(<App />);
    await upload();
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("bad sbom"));

    await userEvent.click(screen.getByTestId("dismiss-error"));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("keeps action buttons disabled after a parse failure (no repeat errors)", async () => {
    parseSbom.mockRejectedValue(new Error("bad sbom"));
    render(<App />);
    await upload();
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("bad sbom"));
    // parsed === null after failure, so Save/Preview must stay disabled.
    expect(screen.getByTestId("save-notice")).toBeDisabled();
    expect(screen.getByTestId("generate-preview")).toBeDisabled();
  });

  it("loads a bundled sample when 'Try a sample' is clicked (U1)", async () => {
    parseSbom.mockResolvedValue(parsed("example-product", 2));
    render(<App />);
    await userEvent.click(screen.getByTestId("try-sample"));
    await waitFor(() => expect(screen.getByText("example-product")).toBeInTheDocument());
    const arg = parseSbom.mock.calls[0][0] as File;
    expect(arg.name).toBe("example.spdx.json");
  });

  it("clears everything when the file is removed", async () => {
    parseSbom.mockResolvedValue(parsed("demo", 1));
    render(<App />);
    await upload();
    await waitFor(() => screen.getByText("demo"));

    await userEvent.click(screen.getByTestId("clear-file"));
    expect(screen.queryByText("demo")).not.toBeInTheDocument();
    expect(screen.getByTestId("save-notice")).toBeDisabled();
  });

  it("adds a recovery hint for an unsupported-file error (U5)", async () => {
    parseSbom.mockRejectedValue(new Error("unsupported or unrecognized SBOM format: x.json"));
    render(<App />);
    await upload("x.json");
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(/make sure the file is an sbom/i),
    );
  });

  it("saves with the backend-provided filename and revokes the object URL", async () => {
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
    await upload();
    await waitFor(() => screen.getByText("demo"));
    await userEvent.click(screen.getByTestId("save-notice"));

    await waitFor(() => expect(createUrl).toHaveBeenCalled());
    expect(anchor?.download).toBe("OSS_Notice_demo.html");
    expect(renderNotice).toHaveBeenCalledWith(
      expect.any(File),
      expect.objectContaining({ format: "html", download: true }),
    );
    await waitFor(() => expect(revokeUrl).toHaveBeenCalledWith("blob:mock"));
  });

  it("saves every selected format in turn", async () => {
    parseSbom.mockResolvedValue(parsed("demo", 1));
    renderNotice.mockResolvedValue({ blob: new Blob(["x"]), filename: "OSS_Notice_demo.html" });
    Object.defineProperty(URL, "createObjectURL", { value: vi.fn(() => "blob:m"), configurable: true });
    Object.defineProperty(URL, "revokeObjectURL", { value: vi.fn(), configurable: true });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    render(<App />);
    await upload();
    await waitFor(() => screen.getByText("demo"));
    await userEvent.click(screen.getByLabelText("Markdown"));
    expect(screen.getByTestId("save-notice")).toHaveTextContent("Save 2 notices");
    await userEvent.click(screen.getByTestId("save-notice"));

    await waitFor(() => expect(renderNotice).toHaveBeenCalledTimes(2));
    expect(renderNotice.mock.calls.map(([, opts]) => opts.format)).toEqual(["html", "markdown"]);
  });

  it("uses the Electron printToPDF bridge for pdf, naming it like the other formats", async () => {
    parseSbom.mockResolvedValue(parsed("demo", 1));
    // jsdom does not support Blob.text() -> replace with a blob-like object that provides text()
    const blob = { text: async () => "<html>notice</html>" } as unknown as Blob;
    renderNotice.mockResolvedValue({ blob, filename: "OSS_Notice_demo.html" });
    const exportPdf = vi.fn().mockResolvedValue({ saved: true, path: "/tmp/OSS_Notice_demo.pdf" });
    (window as Window & { onot?: unknown }).onot = { exportPdf };

    render(<App />);
    await upload();
    await waitFor(() => screen.getByText("demo"));
    await userEvent.click(screen.getByLabelText("HTML")); // leave pdf as the only format
    await userEvent.click(screen.getByLabelText("PDF"));
    await userEvent.click(screen.getByTestId("save-notice"));

    await waitFor(() => expect(exportPdf).toHaveBeenCalled());
    // Renders HTML and hands it to printToPDF, not a sidecar PDF. download is what makes the
    // backend send Content-Disposition, and that header is the only source of the real filename.
    expect(renderNotice).toHaveBeenCalledWith(
      expect.any(File),
      expect.objectContaining({ format: "html", download: true }),
    );
    expect(exportPdf.mock.calls[0][1]).toBe("OSS_Notice_demo.pdf");
    await waitFor(() =>
      expect(screen.getByTestId("save-banner")).toHaveTextContent("/tmp/OSS_Notice_demo.pdf"),
    );
  });

  it("tells the user when a PDF save is cancelled (U7)", async () => {
    parseSbom.mockResolvedValue(parsed("demo", 1));
    const blob = { text: async () => "<html>notice</html>" } as unknown as Blob;
    renderNotice.mockResolvedValue({ blob, filename: "x.html" });
    const exportPdf = vi.fn().mockResolvedValue({ saved: false });
    (window as Window & { onot?: unknown }).onot = { exportPdf };

    render(<App />);
    await upload();
    await waitFor(() => screen.getByText("demo"));
    await userEvent.click(screen.getByLabelText("HTML"));
    await userEvent.click(screen.getByLabelText("PDF"));
    await userEvent.click(screen.getByTestId("save-notice"));

    await waitFor(() =>
      expect(screen.getByTestId("save-banner")).toHaveTextContent(/save cancelled/i),
    );
  });

  it("offers Show in folder once a path is known", async () => {
    parseSbom.mockResolvedValue(parsed("demo", 1));
    const blob = { text: async () => "<html>notice</html>" } as unknown as Blob;
    renderNotice.mockResolvedValue({ blob, filename: "x.html" });
    const showItemInFolder = vi.fn();
    (window as Window & { onot?: unknown }).onot = {
      exportPdf: vi.fn().mockResolvedValue({ saved: true, path: "/tmp/n.pdf" }),
      showItemInFolder,
    };

    render(<App />);
    await upload();
    await waitFor(() => screen.getByText("demo"));
    await userEvent.click(screen.getByLabelText("HTML"));
    await userEvent.click(screen.getByLabelText("PDF"));
    await userEvent.click(screen.getByTestId("save-notice"));

    await waitFor(() => expect(screen.getByTestId("show-in-folder")).toBeInTheDocument());
    await userEvent.click(screen.getByTestId("show-in-folder"));
    expect(showItemInFolder).toHaveBeenCalledWith("/tmp/n.pdf");
  });

  it("remembers the notice details only when asked", async () => {
    render(<App />);
    await userEvent.type(screen.getByLabelText("Organization"), "Acme");
    expect(localStorage.getItem("onot.company")).toBeNull();

    await userEvent.click(screen.getByLabelText("Remember these details"));
    await waitFor(() =>
      expect(localStorage.getItem("onot.company")).toContain("Acme"),
    );
  });
});
