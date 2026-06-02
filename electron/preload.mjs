// 렌더러에 안전한 브리지만 노출(contextIsolation). PDF 내보내기를 메인에 위임.
import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("onot", {
  exportPdf: (html, suggestedName) => ipcRenderer.invoke("export-pdf", html, suggestedName),
});
