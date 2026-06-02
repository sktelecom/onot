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
    // color-contrast는 jsdom에 실제 렌더링 색/canvas가 없어 신뢰할 수 없다.
    // 이 룰을 끄지 않으면 getContext 미구현으로 incomplete 처리되며 조용히 누락된다.
    // 명도 대비 검증은 실제 브라우저가 있는 Playwright-electron E2E의 책임으로 위임한다.
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

  it("downloads with the backend-provided filename and revokes the object URL", async () => {
    parseSbom.mockResolvedValue(parsed("demo", 1));
    renderNotice.mockResolvedValue({ blob: new Blob(["x"]), filename: "OSS_Notice_demo.html" });
    const createUrl = vi.fn(() => "blob:mock");
    const revokeUrl = vi.fn();
    // jsdom에는 createObjectURL/revokeObjectURL이 없으므로 직접 정의
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
    // jsdom Blob.text() 미지원 → text()를 제공하는 blob-유사 객체로 대체
    const blob = { text: async () => "<html>notice</html>" } as unknown as Blob;
    renderNotice.mockResolvedValue({ blob, filename: "x.html" });
    const exportPdf = vi.fn().mockResolvedValue({ saved: true });
    (window as Window & { onot?: unknown }).onot = { exportPdf };

    render(<App />);
    await userEvent.upload(screen.getByTestId("file-input"), new File(["x"], "demo.spdx.json"));
    await waitFor(() => screen.getByText("demo"));
    await userEvent.click(screen.getByLabelText("pdf")); // 설정에서 pdf 포맷 추가
    await userEvent.click(screen.getByRole("button", { name: /download pdf/i }));

    await waitFor(() => expect(exportPdf).toHaveBeenCalled());
    // 사이드카 PDF가 아니라 HTML을 렌더해 printToPDF로 넘긴다
    expect(renderNotice).toHaveBeenCalledWith(
      expect.any(File),
      expect.objectContaining({ format: "html" }),
    );
  });
});
