// Bridge exposed by the Electron preload (only present in the installable desktop app).
interface OnotBridge {
  exportPdf: (html: string, suggestedName?: string) => Promise<{ saved: boolean; path?: string }>;
}

interface Window {
  onot?: OnotBridge;
}
