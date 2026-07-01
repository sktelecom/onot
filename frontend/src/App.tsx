import { useState } from "react";
import sampleSpdx from "./assets/example.spdx.json?raw";
import { FileDropzone } from "./components/FileDropzone";
import { Preview } from "./components/Preview";
import { type NoticeSettings, SettingsPanel } from "./components/SettingsPanel";
import { Button } from "./components/ui/Button";
import { Card, CardTitle } from "./components/ui/Card";
import { parseSbom, type ParseResult, renderNotice } from "./lib/api";
import { type MessageKey, t, type UiLang } from "./lib/i18n";

// Map a raw backend error message to an actionable hint key (recovery guidance for novices).
function errorHintKey(message: string): MessageKey | null {
  if (/unsupported or unrecognized/i.test(message)) return "errFormat";
  if (/failed to (parse|open)/i.test(message)) return "errParse";
  if (/too large/i.test(message)) return "errTooLarge";
  if (/empty upload/i.test(message)) return "errEmpty";
  if (/failed to fetch|networkerror|load failed/i.test(message)) return "errEngine";
  return null;
}

export default function App() {
  const uiLang: UiLang = "en";
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
  const [info, setInfo] = useState("");

  async function handleFile(f: File) {
    setFile(f);
    setParsed(null);
    setPreviewHtml("");
    setError("");
    setInfo("");
    setStatus("parsing");
    try {
      setParsed(await parseSbom(f));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setStatus("idle");
    }
  }

  // Load a bundled example SBOM so first-time users can try the flow without their own file.
  function handleTrySample() {
    handleFile(new File([sampleSpdx], "example.spdx.json", { type: "application/json" }));
  }

  async function handleGenerate() {
    if (!file) return;
    setStatus("rendering");
    setError("");
    setInfo("");
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
    setInfo("");
    try {
      // Installed (Electron): generate PDF via printToPDF, not the sidecar (S5).
      if (format === "pdf" && window.onot?.exportPdf) {
        const { blob } = await renderNotice(file, {
          format: "html",
          lang: settings.lang,
          company: settings.company,
        });
        const res = await window.onot.exportPdf(await blob.text(), "OSS_Notice.pdf");
        // A cancelled Save dialog should not look like nothing happened.
        if (res && res.saved === false) setInfo(t(uiLang, "pdfCancelled"));
        return;
      }
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
      // defer URL revocation asynchronously so the download can start (sync revoke risks cancelling it)
      setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">{t(uiLang, "title")}</h1>
        <p className="text-sm text-zinc-400">{t(uiLang, "subtitle")}</p>
      </header>

      <main>
        {error && (
          <div
            role="alert"
            className="mb-4 rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
          >
            <div>
              {t(uiLang, "error")}: {error}
            </div>
            {errorHintKey(error) && (
              <div className="mt-1 text-xs opacity-90">{t(uiLang, errorHintKey(error)!)}</div>
            )}
          </div>
        )}

        {info && (
          <div
            role="status"
            className="mb-4 rounded-md border border-zinc-300 bg-zinc-50 p-3 text-sm text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300"
          >
            {info}
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-[1fr_360px]">
        <div className="space-y-4">
          <FileDropzone lang={uiLang} onFile={handleFile} fileName={file?.name} />
          {status === "parsing" && (
            <p className="text-sm text-zinc-400">{t(uiLang, "parsing")}</p>
          )}
          {!file && status === "idle" && (
            <div className="flex items-center gap-3">
              <p className="text-sm text-zinc-400">{t(uiLang, "noFile")}</p>
              <Button
                variant="secondary"
                data-testid="try-sample"
                onClick={handleTrySample}
              >
                {t(uiLang, "trySample")}
              </Button>
            </div>
          )}
          {parsed && (
            <Card>
              <CardTitle>{parsed.document.name}</CardTitle>
              <p className="text-sm text-zinc-400">
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
              <Button
                data-testid="generate-preview"
                onClick={handleGenerate}
                disabled={!parsed || status !== "idle"}
              >
                {status === "rendering" ? t(uiLang, "rendering") : t(uiLang, "generate")}
              </Button>
              <div className="flex flex-wrap gap-2">
                {settings.formats.map((fmt) => (
                  <Button
                    key={fmt}
                    variant="secondary"
                    onClick={() => handleDownload(fmt)}
                    disabled={!parsed}
                  >
                    {t(uiLang, "download")} {fmt}
                  </Button>
                ))}
              </div>
              {settings.formats.length === 0 && (
                <p className="text-xs text-zinc-400">{t(uiLang, "noFormats")}</p>
              )}
              {!parsed && (
                <p className="text-xs text-zinc-400">{t(uiLang, "uploadFirst")}</p>
              )}
            </div>
          </Card>
        </div>
        </div>
      </main>
    </div>
  );
}
