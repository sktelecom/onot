// Bridge exposed by the Electron preload (only present in the installable desktop app).
interface OpenedSbom {
  name: string;
  data: ArrayBuffer;
}

// Everything past exportPdf is optional so the renderer keeps working against an older preload,
// which is also why the app reaches for these through `?.`. A packaged build ships both halves
// together and has all of them.
interface OnotBridge {
  exportPdf: (html: string, suggestedName?: string) => Promise<{ saved: boolean; path?: string }>;
  /** Resolves once the sidecar is listening. The window opens before that happens. */
  getApiBase?: () => Promise<string>;
  showItemInFolder?: (filePath: string) => Promise<boolean>;
  setWindowTitle?: (title: string) => Promise<void>;
  /** Registers a listener and returns its unsubscribe function. */
  onOpenSbom?: (callback: (file: OpenedSbom) => void) => () => void;
  onSaveNotice?: (callback: () => void) => () => void;
  /** A plain download (html, text, markdown) finished; the argument is where it landed. */
  onDownloadDone?: (callback: (path: string) => void) => () => void;
  onDownloadCancelled?: (callback: () => void) => () => void;
}

interface Window {
  onot?: OnotBridge;
}
