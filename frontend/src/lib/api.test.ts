// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchFormats, parseSbom, renderNotice, resolveApiBase } from "./api";

function mockFetch(impl: (url: string, init?: RequestInit) => Response) {
  vi.stubGlobal("fetch", vi.fn((url: string, init?: RequestInit) => Promise.resolve(impl(url, init))));
}

afterEach(() => vi.unstubAllGlobals());

const file = new File(["data"], "sbom.json", { type: "application/json" });

describe("resolveApiBase", () => {
  afterEach(() => history.replaceState({}, "", "/"));

  it("reads apiBase from the URL query (Electron injects the sidecar port)", () => {
    history.replaceState({}, "", "/?apiBase=http://127.0.0.1:9999");
    expect(resolveApiBase()).toBe("http://127.0.0.1:9999");
  });

  it("falls back to same-origin when no query is present", () => {
    history.replaceState({}, "", "/");
    expect(resolveApiBase()).toBe("");
  });
});

describe("api client", () => {
  it("fetchFormats returns formats", async () => {
    mockFetch(() => new Response(JSON.stringify({ output: ["html"], input: ["spdx"] }), { status: 200 }));
    expect(await fetchFormats()).toEqual({ output: ["html"], input: ["spdx"] });
  });

  it("parseSbom posts multipart and returns result", async () => {
    let captured: RequestInit | undefined;
    mockFetch((url, init) => {
      captured = init;
      expect(url).toContain("/api/parse");
      return new Response(JSON.stringify({ document: { name: "p", packages: [], licenses: [] }, warnings: [] }), { status: 200 });
    });
    const result = await parseSbom(file);
    expect(result.document.name).toBe("p");
    expect(captured?.method).toBe("POST");
    expect(captured?.body).toBeInstanceOf(FormData);
  });

  it("renderNotice returns a blob and the backend filename", async () => {
    mockFetch(
      () =>
        new Response("<html>notice</html>", {
          status: 200,
          headers: {
            "content-type": "text/html",
            "content-disposition": 'attachment; filename="OSS_Notice_demo.html"',
          },
        }),
    );
    const { blob, filename } = await renderNotice(file, { format: "html", lang: "en" });
    // size는 realm/Node 버전에 무관한 안정 속성(instanceof Blob은 realm 차이로 불안정)
    expect(blob.size).toBeGreaterThan(0);
    expect(filename).toBe("OSS_Notice_demo.html");
  });

  it("renderNotice falls back to a default filename without Content-Disposition", async () => {
    mockFetch(() => new Response("# notice", { status: 200 }));
    const { filename } = await renderNotice(file, { format: "markdown", lang: "en" });
    expect(filename).toBe("OSS_Notice.md");
  });

  it("throws with server detail on error", async () => {
    mockFetch(() => new Response(JSON.stringify({ detail: "unsupported format" }), { status: 400 }));
    await expect(parseSbom(file)).rejects.toThrow("unsupported format");
  });
});
