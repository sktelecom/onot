// Electron main process: window → sidecar → printToPDF → graceful shutdown.
// ESM (Electron >= 28). Real startup/E2E is verified in M9 CI (Playwright-electron).
import { app, BrowserWindow, dialog, ipcMain, screen, session, shell } from "electron";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { installMenu } from "./lib/menu.mjs";
import { findFreePort, Sidecar } from "./lib/sidecar.mjs";
import { createWindowState, MIN_SIZE } from "./lib/window-state.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const isDev = !app.isPackaged;
const isMac = process.platform === "darwin";
const isWin = process.platform === "win32";
const MAX_PDF_HTML = 20 * 1024 * 1024;

// 2cm in inches, matching the @page margin the CLI's WeasyPrint stylesheet uses.
const PDF_MARGIN_IN = 0.7874;

let sidecar = null;
let mainWindow = null;
let appOrigin = "file://";
// Set as soon as a quit begins. The window now opens before the sidecar is up, so a quit can
// land in the middle of startup; without this the failed start would raise its Retry dialog on
// the way out and the app would never finish quitting.
let quitting = false;

function sidecarCommand() {
  if (isDev) {
    // CI/alternate environments override the python path via ONOT_SIDECAR_PYTHON (default: local .venv)
    const python =
      process.env.ONOT_SIDECAR_PYTHON ??
      path.resolve(here, "..", ".venv", "bin", isWin ? "python.exe" : "python");
    return { command: python, args: ["-m", "onot.api.serve"] };
  }
  const bin = isWin ? "onot-sidecar.exe" : "onot-sidecar";
  return { command: path.join(process.resourcesPath, "sidecar", "onot-sidecar", bin), args: [] };
}

const SIDECAR_LOG = path.join(app.getPath("userData"), "sidecar.log");
// Windows Defender scans a freshly-built unsigned exe on first launch, which can push startup
// past the macOS-tuned budget; give Windows a longer first-run window.
const SIDECAR_TIMEOUT_MS = isWin ? 120000 : 40000;

async function startSidecar() {
  const port = await findFreePort();
  const { command, args } = sidecarCommand();
  sidecar = new Sidecar({ command, args, port, logPath: SIDECAR_LOG });
  await sidecar.start({ timeoutMs: SIDECAR_TIMEOUT_MS });
  return port;
}

// The window opens before the sidecar is up, so the renderer asks for the base URL and this
// promise answers once there is one. Waiting here rather than holding the window back is what
// keeps a slow first run (up to two minutes on Windows) from looking like a failure to launch.
let resolveApiBase;
const apiBaseReady = new Promise((resolve) => {
  resolveApiBase = resolve;
});

// Security: block new windows and navigation to external origins (external links open in the system browser).
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

async function createWindow() {
  const workAreas = screen.getAllDisplays().map((display) => display.workArea);
  const windowState = createWindowState({ userDataDir: app.getPath("userData"), workAreas });

  mainWindow = new BrowserWindow({
    ...windowState.bounds,
    minWidth: MIN_SIZE.width,
    minHeight: MIN_SIZE.height,
    backgroundColor: "#0a0a0b",
    webPreferences: {
      preload: path.join(here, "preload.mjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false, // uses ESM preload
    },
  });
  if (windowState.bounds.maximized) mainWindow.maximize();
  windowState.track(mainWindow);

  // ONOT_FRONTEND_DIR overrides the frontend location and forces the packaged-style file://
  // load even when unpackaged. The file:// render E2E uses it to exercise the production path
  // that dev-mode E2E (http://) cannot cover — the blank-screen class of bug (#68).
  const frontendDir = process.env.ONOT_FRONTEND_DIR;
  if (isDev && !frontendDir) {
    const base = process.env.VITE_DEV_SERVER ?? "http://localhost:5173";
    appOrigin = base;
    await mainWindow.loadURL(base);
  } else {
    const dir = frontendDir ?? path.join(process.resourcesPath, "frontend");
    await mainWindow.loadFile(path.join(dir, "index.html"));
  }
}

function sendToRenderer(channel, payload) {
  if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send(channel, payload);
}

// File > Open SBOM. Main owns the dialog and hands the bytes over, so the renderer keeps a
// single path for a file however it arrived (drop, browse, or this menu item).
async function openSbomFromMenu() {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ["openFile"],
    filters: [
      { name: "SBOM", extensions: ["spdx", "json", "yaml", "yml", "xml", "rdf", "xlsx"] },
      { name: "All Files", extensions: ["*"] },
    ],
  });
  if (canceled || filePaths.length === 0) return;
  try {
    const data = await fs.readFile(filePaths[0]);
    sendToRenderer("menu:open-sbom", { name: path.basename(filePaths[0]), data: data.buffer });
  } catch (err) {
    dialog.showMessageBox(mainWindow, {
      type: "error",
      title: "onot",
      message: "Couldn't read that file.",
      detail: err.message,
    });
  }
}

function showAbout() {
  dialog.showMessageBox(mainWindow ?? undefined, {
    type: "info",
    title: "About onot",
    message: `onot ${app.getVersion()}`,
    detail:
      "Generates open source notices from SBOM documents, offline.\n" +
      "Jointly developed by Kakao and SK telecom.",
    buttons: ["OK"],
  });
}

// Convert HTML sent by the renderer into a PDF in an isolated offscreen window (S5: desktop PDF = printToPDF).
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
      javascript: false, // JS not needed for PDF rendering — entirely blocks script execution within the data URL
    },
  });
  try {
    await offscreen.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    // Page geometry and the numbered footer match the CLI's pdf.css, so the two routes to a PDF
    // produce the same document. The page-break rules come from the @media print block that the
    // notice already carries, which Chromium and WeasyPrint both honour.
    const pdf = await offscreen.webContents.printToPDF({
      printBackground: true,
      pageSize: "A4",
      margins: {
        top: PDF_MARGIN_IN,
        bottom: PDF_MARGIN_IN,
        left: PDF_MARGIN_IN,
        right: PDF_MARGIN_IN,
      },
      displayHeaderFooter: true,
      headerTemplate: "<span></span>",
      footerTemplate:
        '<div style="width:100%;font-size:9pt;color:#6b7280;text-align:center;">' +
        '<span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    });
    const safeName = path.basename(
      typeof suggestedName === "string" && suggestedName ? suggestedName : "OSS_Notice.pdf",
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

ipcMain.handle("get-api-base", () => apiBaseReady);

// Reveal a saved notice in Explorer or Finder. Only ever called with a path this process just
// wrote through the save dialog.
ipcMain.handle("show-item-in-folder", (_event, filePath) => {
  if (typeof filePath !== "string" || !filePath) return false;
  shell.showItemInFolder(path.resolve(filePath));
  return true;
});

ipcMain.handle("set-window-title", (_event, title) => {
  if (typeof title === "string" && mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.setTitle(title);
  }
});

// Sidecar cleanup: unified into an idempotent promise so it runs exactly once even under shutdown races.
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
  // Security: apply CSP to all responses (connections limited to the local sidecar).
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
  // html, text and markdown go out as ordinary downloads, so their destination is only known
  // once Electron's save dialog closes. Observing it is what lets the app say where the notice
  // landed instead of leaving the save silent.
  session.defaultSession.on("will-download", (_event, item) => {
    item.once("done", (_doneEvent, state) => {
      if (state === "completed") sendToRenderer("download:done", item.getSavePath());
      else sendToRenderer("download:cancelled");
    });
  });
  installMenu({
    isDev,
    isMac,
    onOpenSbom: openSbomFromMenu,
    onSaveNotice: () => sendToRenderer("menu:save-notice"),
    onAbout: showAbout,
  });
  await createWindow();
  await launchWithRetry();
});

// Start the sidecar; on failure show an actionable Retry/Quit dialog (with the log path) instead
// of quitting silently, since a slow first-run antivirus scan is recoverable. The window is
// already up by this point and shows its own starting state.
async function launchWithRetry() {
  for (;;) {
    if (quitting) return;
    try {
      const port = await startSidecar();
      if (quitting) {
        await shutdown();
        return;
      }
      resolveApiBase(`http://127.0.0.1:${port}`);
      return;
    } catch (err) {
      await shutdown(); // tear down any half-started sidecar before retrying
      shutdownPromise = null; // re-arm so the next start is not short-circuited
      if (quitting) return; // the start was interrupted by the quit, not by a real failure
      const choice = dialog.showMessageBoxSync({
        type: "error",
        title: "onot",
        message: "Couldn't start onot's local engine.",
        detail:
          `${err.message}\n\n` +
          "On Windows, antivirus scanning a fresh unsigned build can make the first launch slow " +
          "or block it. You can retry, or check the log for details:\n" +
          SIDECAR_LOG,
        buttons: ["Retry", "Quit"],
        defaultId: 0,
        cancelId: 1,
      });
      if (choice !== 0) {
        app.quit();
        return;
      }
    }
  }
}

app.on("window-all-closed", () => {
  quitting = true;
  shutdown().finally(() => app.quit());
});

let quitHandled = false;
app.on("before-quit", (event) => {
  quitting = true;
  if (quitHandled) return;
  event.preventDefault();
  quitHandled = true;
  shutdown().finally(() => app.quit());
});
