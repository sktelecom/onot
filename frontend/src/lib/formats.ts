// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Identifier as the API knows it, paired with the spelling a reader expects to see. The screen
// used to show the raw identifiers ("html", "pdf"), which read as code rather than as formats.
export const ALL_FORMATS = [
  { id: "html", label: "HTML" },
  { id: "text", label: "Text" },
  { id: "markdown", label: "Markdown" },
  { id: "pdf", label: "PDF" },
] as const;

export type FormatId = (typeof ALL_FORMATS)[number]["id"];

export function formatLabel(id: string): string {
  return ALL_FORMATS.find((format) => format.id === id)?.label ?? id;
}

const EXTENSIONS: Record<string, string> = { markdown: "md", text: "txt" };

export function extensionOf(id: string): string {
  return EXTENSIONS[id] ?? id;
}

/** Reuse the backend's filename for the PDF too, so every format lands with the same name. */
export function pdfNameFrom(htmlFilename: string): string {
  return htmlFilename.replace(/\.html?$/i, "") + ".pdf";
}
