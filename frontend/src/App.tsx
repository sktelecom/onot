import { useState } from "react";
import { FileDropzone } from "./components/FileDropzone";
import { Preview } from "./components/Preview";
import { type NoticeSettings, SettingsPanel } from "./components/SettingsPanel";
import { Button } from "./components/ui/Button";
import { Card, CardTitle } from "./components/ui/Card";
import { parseSbom, type ParseResult, renderNotice } from "./lib/api";
import { t, type UiLang } from "./lib/i18n";

export default function App() {
  const [uiLang, setUiLang] = useState<UiLang>("en");
  const [file, setFile] = useState<File | null>(null);
  const [parsed, setParsed] = useState<ParseResult | null>(null);
  const [settings, setSettings] = useState<NoticeSettings>({
    formats: ["html"],
    lang: "en",
    company: {},
  });
  const [previewHtml, setPreviewHtml] = useState("");
  const [status, setStatus] = useState<"idle" | "parsing" | "rendering">("idle");
  const [error, setError] = useState("");

  async function handleFile(f: File) {
    setFile(f);
    setParsed(null);
    setPreviewHtml("");
    setError("");
    setStatus("parsing");
    try {
      setParsed(await parseSbom(f));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setStatus("idle");
    }
  }

  async function handleGenerate() {
    if (!file) return;
    setStatus("rendering");
    setError("");
    try {
      const { blob } = await renderNotice(file, {
        format: "html",
        lang: settings.lang,
        company: settings.company,
      });
      setPreviewHtml(await blob.text());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setStatus("idle");
    }
  }

  async function handleDownload(format: string) {
    if (!file) return;
    setError("");
    try {
      const { blob, filename } = await renderNotice(file, {
        format,
        lang: settings.lang,
        download: true,
        company: settings.company,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      // 다운로드가 시작되도록 URL 해제는 비동기로 미룬다(동기 해제 시 취소 위험)
      setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <header className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{t(uiLang, "title")}</h1>
          <p className="text-sm text-zinc-500">{t(uiLang, "subtitle")}</p>
        </div>
        <select
          aria-label="UI language"
          value={uiLang}
          onChange={(e) => setUiLang(e.target.value as UiLang)}
          className="rounded-md border border-zinc-300 bg-transparent px-2 py-1 text-sm dark:border-zinc-700"
        >
          <option value="en">EN</option>
          <option value="ko">KO</option>
        </select>
      </header>

      <main>
        {error && (
          <div
            role="alert"
            className="mb-4 rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
          >
            {t(uiLang, "error")}: {error}
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-[1fr_360px]">
        <div className="space-y-4">
          <FileDropzone lang={uiLang} onFile={handleFile} fileName={file?.name} />
          {status === "parsing" && (
            <p className="text-sm text-zinc-500">{t(uiLang, "parsing")}</p>
          )}
          {!file && status === "idle" && (
            <p className="text-sm text-zinc-500">{t(uiLang, "noFile")}</p>
          )}
          {parsed && (
            <Card>
              <CardTitle>{parsed.document.name}</CardTitle>
              <p className="text-sm text-zinc-500">
                {parsed.document.packages.length} {t(uiLang, "components")}
              </p>
              {parsed.warnings.length > 0 && (
                <ul className="mt-2 list-disc pl-5 text-xs text-amber-600">
                  {parsed.warnings.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              )}
            </Card>
          )}
          {previewHtml && (
            <Card>
              <CardTitle>{t(uiLang, "preview")}</CardTitle>
              <Preview html={previewHtml} title={t(uiLang, "preview")} />
            </Card>
          )}
        </div>

        <div className="space-y-4">
          <SettingsPanel uiLang={uiLang} value={settings} onChange={setSettings} />
          <Card>
            <div className="flex flex-col gap-2">
              <Button onClick={handleGenerate} disabled={!file || status !== "idle"}>
                {status === "rendering" ? t(uiLang, "rendering") : t(uiLang, "generate")}
              </Button>
              <div className="flex flex-wrap gap-2">
                {settings.formats.map((fmt) => (
                  <Button
                    key={fmt}
                    variant="secondary"
                    onClick={() => handleDownload(fmt)}
                    disabled={!file}
                  >
                    {t(uiLang, "download")} {fmt}
                  </Button>
                ))}
              </div>
            </div>
          </Card>
        </div>
        </div>
      </main>
    </div>
  );
}
