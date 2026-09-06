import { Loader2, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import logoMark from "./assets/logo-mark.svg";
import sampleSpdx from "./assets/example.spdx.json?raw";
import { FileDropzone } from "./components/FileDropzone";
import { OutputPanel } from "./components/OutputPanel";
import { ParseSummary } from "./components/ParseSummary";
import { Preview } from "./components/Preview";
import { type NoticeSettings, SettingsPanel } from "./components/SettingsPanel";
import { ThemeToggle } from "./components/ThemeToggle";
import { Button } from "./components/ui/Button";
import { parseSbom, type ParseResult, renderNotice, waitForApi } from "./lib/api";
import { pdfNameFrom } from "./lib/formats";
import { t, tf, type MessageKey, type UiLang } from "./lib/i18n";
import { readCompany, readRemember, saveCompany } from "./lib/notice-settings";

// Map a raw backend error message to an actionable hint key (recovery guidance for novices).
function errorHintKey(message: string): MessageKey | null {
  if (/unsupported or unrecognized/i.test(message)) return "errFormat";
  if (/failed to (parse|open)/i.test(message)) return "errParse";
  if (/too large/i.test(message)) return "errTooLarge";
  if (/empty upload/i.test(message)) return "errEmpty";
  if (/failed to fetch|networkerror|load failed/i.test(message)) return "errEngine";
  return null;
}

type Status = "idle" | "parsing" | "rendering" | "saving";
interface Banner {
  kind: "info" | "success";
  text: string;
  path?: string;
}

export default function App() {
  const uiLang: UiLang = "en";
  const [file, setFile] = useState<File | null>(null);
  const [parsed, setParsed] = useState<ParseResult | null>(null);
  const [settings, setSettings] = useState<NoticeSettings>(() => ({
    formats: ["html"],
    lang: "en",
    company: readCompany(),
    remember: readRemember(),
  }));
  const [previewHtml, setPreviewHtml] = useState("");
  // The window opens before the local engine is listening, so the app has a state for "not yet".
  // It is informational only: a request made now simply waits for the engine to come up.
  const [engineReady, setEngineReady] = useState(false);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");
  const [banner, setBanner] = useState<Banner | null>(null);

  useEffect(() => {
    let active = true;
    waitForApi().then(() => {
      if (active) setEngineReady(true);
    });
    return () => {
      active = false;
    };
  }, []);

  // Only persisted once asked for; these values end up in a published document.
  useEffect(() => {
    saveCompany(settings.company, settings.remember);
  }, [settings.company, settings.remember]);

  // Name the window after the file in hand, the way an editor does.
  useEffect(() => {
    const title = file ? `${file.name} - ${t(uiLang, "appName")}` : t(uiLang, "appName");
    document.title = title;
    window.onot?.setWindowTitle?.(title);
  }, [file, uiLang]);

  const handleFile = useCallback(async (f: File) => {
    setFile(f);
    setParsed(null);
    setPreviewHtml("");
    setError("");
    setBanner(null);
    setStatus("parsing");
    try {
      setParsed(await parseSbom(f));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setStatus("idle");
    }
  }, []);

  function clearFile() {
    setFile(null);
    setParsed(null);
    setPreviewHtml("");
    setError("");
    setBanner(null);
  }

  // Load a bundled example SBOM so first-time users can try the flow without their own file.
  function handleTrySample() {
    handleFile(new File([sampleSpdx], "example.spdx.json", { type: "application/json" }));
  }

  async function handlePreview() {
    if (!file) return;
    setStatus("rendering");
    setError("");
    setBanner(null);
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

  // One format. Returns the saved path when this route knows it: the desktop PDF export reports
  // back directly, while a browser-style download only reveals its path through will-download,
  // which the effect below listens for.
  async function saveFormat(
    source: File,
    format: string,
  ): Promise<{ cancelled?: boolean; path?: string }> {
    // Installed (Electron): generate PDF via printToPDF, not the sidecar (S5).
    if (format === "pdf" && window.onot?.exportPdf) {
      const { blob, filename } = await renderNotice(source, {
        format: "html",
        lang: settings.lang,
        // download only adds Content-Disposition, which is where the product-based filename
        // comes from. Without it the PDF fell back to a bare "OSS_Notice.pdf" while every other
        // format carried the product name and a timestamp.
        download: true,
        company: settings.company,
      });
      const res = await window.onot.exportPdf(await blob.text(), pdfNameFrom(filename));
      if (res && res.saved === false) return { cancelled: true };
      return { path: res?.path };
    }
    const { blob, filename } = await renderNotice(source, {
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
    return {};
  }

  async function handleSave() {
    if (!file || settings.formats.length === 0 || status !== "idle") return;
    setError("");
    setBanner(null);
    setStatus("saving");
    const paths: string[] = [];
    try {
      for (const format of settings.formats) {
        const result = await saveFormat(file, format);
        if (result.cancelled) {
          setBanner({ kind: "info", text: t(uiLang, "saveCancelled") });
          return;
        }
        if (result.path) paths.push(result.path);
      }
      if (paths.length > 0) {
        setBanner({ kind: "success", text: tf(uiLang, "savedTo", { path: paths[0] }), path: paths[0] });
      } else if (!window.onot) {
        // A browser download reports no destination; say it happened without inventing a path.
        setBanner({ kind: "success", text: t(uiLang, "save") });
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setStatus("idle");
    }
  }

  // The menu drives the same handlers as the buttons. Refs keep the listeners registered once
  // while still calling the current closure over state.
  const saveRef = useRef(handleSave);
  saveRef.current = handleSave;

  useEffect(() => {
    const bridge = window.onot;
    if (!bridge) return;
    const offOpen = bridge.onOpenSbom?.(({ name, data }) => {
      handleFile(new File([data], name));
    });
    const offSave = bridge.onSaveNotice?.(() => void saveRef.current());
    const offDone = bridge.onDownloadDone?.((path) => {
      setBanner({ kind: "success", text: tf(uiLang, "savedTo", { path }), path });
    });
    const offCancelled = bridge.onDownloadCancelled?.(() => {
      setBanner({ kind: "info", text: t(uiLang, "saveCancelled") });
    });
    return () => {
      offOpen?.();
      offSave?.();
      offDone?.();
      offCancelled?.();
    };
  }, [handleFile, uiLang]);

  return (
    <div className="mx-auto max-w-6xl p-6">
      <header className="mb-6 flex items-center gap-3">
        <img src={logoMark} alt="onot" width={44} height={44} className="shrink-0" />
        <div>
          <h1 className="text-2xl font-bold">{t(uiLang, "title")}</h1>
          <p className="text-sm text-fg-muted">{t(uiLang, "subtitle")}</p>
        </div>
        <div className="ml-auto">
          <ThemeToggle lang={uiLang} />
        </div>
      </header>

      <main>
        {!engineReady && (
          <div
            role="status"
            data-testid="engine-starting"
            className="mb-4 flex items-start gap-3 rounded-control border border-border bg-surface-raised p-3 text-sm"
          >
            <Loader2 className="mt-0.5 h-4 w-4 shrink-0 animate-spin text-accent" aria-hidden />
            <div>
              <p className="font-medium">{t(uiLang, "starting")}</p>
              <p className="mt-0.5 text-xs text-fg-muted">{t(uiLang, "startingHint")}</p>
            </div>
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="mb-4 flex items-start gap-3 rounded-control border border-danger-border bg-danger-bg p-3 text-sm text-danger-fg"
          >
            <div className="grow">
              <div>
                {t(uiLang, "error")}: {error}
              </div>
              {errorHintKey(error) && (
                <div className="mt-1 text-xs opacity-90">{t(uiLang, errorHintKey(error)!)}</div>
              )}
            </div>
            <button
              type="button"
              data-testid="dismiss-error"
              aria-label={t(uiLang, "dismiss")}
              onClick={() => setError("")}
              className="shrink-0 rounded-control p-0.5"
            >
              <X className="h-4 w-4" aria-hidden />
            </button>
          </div>
        )}

        {banner && (
          <div
            role="status"
            data-testid="save-banner"
            className="mb-4 flex items-center gap-3 rounded-control border border-border bg-surface-raised p-3 text-sm text-fg"
          >
            <span className="grow break-all">{banner.text}</span>
            {banner.path && window.onot?.showItemInFolder && (
              <Button
                variant="secondary"
                data-testid="show-in-folder"
                className="shrink-0 px-2 py-1 text-xs"
                onClick={() => window.onot?.showItemInFolder?.(banner.path!)}
              >
                {t(uiLang, "showInFolder")}
              </Button>
            )}
            <button
              type="button"
              aria-label={t(uiLang, "dismiss")}
              onClick={() => setBanner(null)}
              className="shrink-0 rounded-control p-0.5 text-fg-muted"
            >
              <X className="h-4 w-4" aria-hidden />
            </button>
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-[1fr_360px]">
          <div className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-fg-muted">
              {t(uiLang, "stepSbom")}
            </h2>
            <FileDropzone lang={uiLang} onFile={handleFile} file={file} onClear={clearFile} />
            {status === "parsing" && (
              <p className="flex items-center gap-2 text-sm text-fg-muted">
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                {t(uiLang, "parsing")}
              </p>
            )}
            {!file && status === "idle" && (
              <div className="flex items-center gap-3">
                <p className="text-sm text-fg-muted">{t(uiLang, "noFile")}</p>
                <Button variant="secondary" data-testid="try-sample" onClick={handleTrySample}>
                  {t(uiLang, "trySample")}
                </Button>
              </div>
            )}
            {parsed && <ParseSummary lang={uiLang} parsed={parsed} />}
            {previewHtml && <Preview lang={uiLang} html={previewHtml} />}
          </div>

          <div className="space-y-4">
            <SettingsPanel uiLang={uiLang} value={settings} onChange={setSettings} />
            <OutputPanel
              uiLang={uiLang}
              value={settings}
              onChange={setSettings}
              onSave={handleSave}
              onPreview={handlePreview}
              ready={parsed !== null}
              saving={status === "saving"}
              rendering={status === "rendering"}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
