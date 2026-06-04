// Electron main process: start sidecar → load window → printToPDF → graceful shutdown.
// ESM (Electron >= 28). Real startup/E2E is verified in M9 CI (Playwright-electron).
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
    // CI/alternate environments override the python path via ONOT_SIDECAR_PYTHON (default: local .venv)
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

async function createWindow(apiBase) {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 860,
    backgroundColor: "#0a0a0b",
    webPreferences: {
      preload: path.join(here, "preload.mjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false, // uses ESM preload
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
