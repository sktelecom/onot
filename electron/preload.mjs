// Expose only a safe bridge to the renderer (contextIsolation). Delegate PDF export to main.
import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("onot", {
  exportPdf: (html, suggestedName) => ipcRenderer.invoke("export-pdf", html, suggestedName),
});
