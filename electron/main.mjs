// Electron 메인 프로세스: 사이드카 기동 → 윈도우 로드 → printToPDF → graceful shutdown.
// ESM(Electron >= 28). 실제 기동/E2E는 M9 CI(Playwright-electron)에서 검증.
import { app, BrowserWindow, dialog, ipcMain, session, shell } from "electron";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { findFreePort, Sidecar } from "./lib/sidecar.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const isDev = !app.isPackaged;
const isWin = process.platform === "win32";
const MAX_PDF_HTML = 20 * 1024 * 1024;

let sidecar = null;
let mainWindow = null;
let appOrigin = "file://";

function sidecarCommand() {
  if (isDev) {
    // CI/대체 환경은 ONOT_SIDECAR_PYTHON으로 python 경로 재정의(기본: 로컬 .venv)
    const python =
      process.env.ONOT_SIDECAR_PYTHON ??
      path.resolve(here, "..", ".venv", "bin", isWin ? "python.exe" : "python");
    return { command: python, args: ["-m", "onot.api.serve"] };
  }
  const bin = isWin ? "onot-sidecar.exe" : "onot-sidecar";
  return { command: path.join(process.resourcesPath, "sidecar", "onot-sidecar", bin), args: [] };
}

async function startSidecar() {
  const port = await findFreePort();
  const { command, args } = sidecarCommand();
  sidecar = new Sidecar({ command, args, port });
  await sidecar.start({ timeoutMs: 40000 });
  return port;
}

// 보안: 신규 창 차단, 외부 출처 네비게이션 차단(외부 링크는 시스템 브라우저로).
function hardenWebContents(contents) {
  contents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("http:") || url.startsWith("https:")) shell.openExternal(url);
    return { action: "deny" };
  });
  contents.on("will-navigate", (event, url) => {
    if (!url.startsWith(appOrigin)) {
      event.preventDefault();
      if (url.startsWith("http:") || url.startsWith("https:")) shell.openExternal(url);
    }
  });
}

async function createWindow(apiBase) {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 860,
    backgroundColor: "#0a0a0b",
    webPreferences: {
      preload: path.join(here, "preload.mjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false, // ESM preload 사용
    },
  });
  if (isDev) {
    const base = process.env.VITE_DEV_SERVER ?? "http://localhost:5173";
    appOrigin = base;
    await mainWindow.loadURL(`${base}?apiBase=${encodeURIComponent(apiBase)}`);
  } else {
    await mainWindow.loadFile(path.join(process.resourcesPath, "frontend", "index.html"), {
      query: { apiBase },
    });
  }
}

// 렌더러가 보낸 HTML을 격리된 오프스크린 창에서 PDF로 변환(S5: 데스크톱 PDF = printToPDF).
ipcMain.handle("export-pdf", async (_event, html, suggestedName) => {
  if (typeof html !== "string" || html.length > MAX_PDF_HTML) {
    throw new Error("invalid PDF source");
  }
  const offscreen = new BrowserWindow({
    show: false,
    webPreferences: {
      offscreen: true,
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      javascript: false, // PDF 렌더에 JS 불필요 — data-URL 내 스크립트 실행 원천 차단
    },
  });
  try {
    await offscreen.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    const pdf = await offscreen.webContents.printToPDF({ printBackground: true, pageSize: "A4" });
    const safeName = path.basename(
      typeof suggestedName === "string" ? suggestedName : "OSS_Notice.pdf",
    );
    const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
      defaultPath: safeName,
      filters: [{ name: "PDF", extensions: ["pdf"] }],
    });
    if (canceled || !filePath) return { saved: false };
    await fs.writeFile(filePath, pdf);
    return { saved: true, path: filePath };
  } finally {
    offscreen.destroy();
  }
});

// 사이드카 정리: 멱등 promise로 단일화해 종료 경합에도 정확히 1회 수행.
let shutdownPromise = null;
function shutdown() {
  if (!shutdownPromise) {
    const current = sidecar;
    sidecar = null;
    shutdownPromise = Promise.resolve(current?.stop());
  }
  return shutdownPromise;
}

app.whenReady().then(async () => {
  app.on("web-contents-created", (_e, contents) => hardenWebContents(contents));
  // 보안: 모든 응답에 CSP 적용(연결은 로컬 사이드카로 한정).
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        "Content-Security-Policy": [
          "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' http://127.0.0.1:* http://localhost:*; frame-src 'self'",
        ],
      },
    });
  });
  try {
    const port = await startSidecar();
    await createWindow(`http://127.0.0.1:${port}`);
  } catch (err) {
    dialog.showErrorBox("onot", `Failed to start the local engine:\n${err.message}`);
    app.quit();
  }
});

app.on("window-all-closed", () => {
  shutdown().finally(() => app.quit());
});

let quitting = false;
app.on("before-quit", (event) => {
  if (quitting) return;
  event.preventDefault();
  quitting = true;
  shutdown().finally(() => app.quit());
});
