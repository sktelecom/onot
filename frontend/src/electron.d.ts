// Electron preload가 노출하는 브리지(설치형 데스크톱에서만 존재).
interface OnotBridge {
  exportPdf: (html: string, suggestedName?: string) => Promise<{ saved: boolean; path?: string }>;
}

interface Window {
  onot?: OnotBridge;
}
