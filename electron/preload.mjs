// Expose only a safe bridge to the renderer (contextIsolation). Delegate privileged work to main.
import { contextBridge, ipcRenderer } from "electron";

// Listener registrations wrap the raw IpcRendererEvent away, so nothing from the main process
// leaks into the renderer's hands beyond the payload itself.
function on(channel, callback) {
  const listener = (_event, payload) => callback(payload);
  ipcRenderer.on(channel, listener);
  return () => ipcRenderer.removeListener(channel, listener);
}

contextBridge.exposeInMainWorld("onot", {
  exportPdf: (html, suggestedName) => ipcRenderer.invoke("export-pdf", html, suggestedName),
  // Resolves once the sidecar is listening; the window is created before that happens.
  getApiBase: () => ipcRenderer.invoke("get-api-base"),
  showItemInFolder: (filePath) => ipcRenderer.invoke("show-item-in-folder", filePath),
  setWindowTitle: (title) => ipcRenderer.invoke("set-window-title", title),
  onOpenSbom: (callback) => on("menu:open-sbom", callback),
  onSaveNotice: (callback) => on("menu:save-notice", callback),
  onDownloadDone: (callback) => on("download:done", callback),
  onDownloadCancelled: (callback) => on("download:cancelled", callback),
});
