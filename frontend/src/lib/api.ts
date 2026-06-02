// onot FastAPI 사이드카 클라이언트. 베이스 URL 우선순위:
// URL 쿼리(?apiBase=, Electron이 동적 포트 주입) > 빌드 환경변수 > 동일 출처("").
export function resolveApiBase(): string {
  if (typeof window !== "undefined" && window.location?.search) {
    const fromQuery = new URLSearchParams(window.location.search).get("apiBase");
    if (fromQuery) return fromQuery;
  }
  return import.meta.env.VITE_API_BASE ?? "";
}

const API_BASE: string = resolveApiBase();

export interface CompanyConfig {
  organization?: string;
  contact_email?: string;
  copyright_holder?: string;
  source_download_url?: string;
}

export interface PackageInfo {
  name: string;
  version: string;
  license_concluded: { raw: string } | null;
  license_declared: { raw: string } | null;
  copyright: { text: string } | null;
}

export interface ParsedDocument {
  name: string;
  packages: PackageInfo[];
  licenses: { license_id: string; name: string }[];
}

export interface ParseResult {
  document: ParsedDocument;
  warnings: string[];
}

export interface Formats {
  output: string[];
  input: string[];
}

async function detail(resp: Response): Promise<string> {
  try {
    const body = await resp.json();
    return typeof body?.detail === "string" ? body.detail : resp.statusText;
  } catch {
    return resp.statusText;
  }
}

const EXT: Record<string, string> = { markdown: "md", text: "txt" };

function filenameFrom(contentDisposition: string | null, format: string): string {
  const match = contentDisposition && /filename="?([^";]+)"?/.exec(contentDisposition);
  return match ? match[1] : `OSS_Notice.${EXT[format] ?? format}`;
}

export async function fetchFormats(): Promise<Formats> {
  const resp = await fetch(`${API_BASE}/api/formats`);
  if (!resp.ok) throw new Error(await detail(resp));
  return resp.json();
}

export async function parseSbom(file: File): Promise<ParseResult> {
  const form = new FormData();
  form.append("file", file);
  const resp = await fetch(`${API_BASE}/api/parse`, { method: "POST", body: form });
  if (!resp.ok) throw new Error(await detail(resp));
  return resp.json();
}

export interface RenderOptions {
  format: string;
  lang: string;
  download?: boolean;
  company?: CompanyConfig;
}

function renderForm(file: File, opts: RenderOptions): FormData {
  const form = new FormData();
  form.append("file", file);
  form.append("format", opts.format);
  form.append("lang", opts.lang);
  form.append("download", String(opts.download ?? false));
  const c = opts.company ?? {};
  form.append("organization", c.organization ?? "");
  form.append("contact_email", c.contact_email ?? "");
  form.append("copyright_holder", c.copyright_holder ?? "");
  form.append("source_download_url", c.source_download_url ?? "");
  return form;
}

export interface RenderedNotice {
  blob: Blob;
  filename: string;
}

export async function renderNotice(file: File, opts: RenderOptions): Promise<RenderedNotice> {
  const resp = await fetch(`${API_BASE}/api/render`, {
    method: "POST",
    body: renderForm(file, opts),
  });
  if (!resp.ok) throw new Error(await detail(resp));
  const blob = await resp.blob();
  // 파일명은 백엔드 Content-Disposition(제품명 기반)을 우선 사용
  const filename = filenameFrom(resp.headers.get("content-disposition"), opts.format);
  return { blob, filename };
}
