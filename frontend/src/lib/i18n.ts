// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// UI label catalog. Separate from the backend notice i18n (these are app-screen strings).
export type UiLang = "en";

export const messages = {
  en: {
    title: "OSS Notice Generator",
    subtitle: "Generate open source notices from SBOM documents — offline.",
    dropzone: "Drop an SBOM file here, or click to browse",
    dropzoneHint: "SPDX (JSON/YAML/Tag-Value/RDF), CycloneDX (JSON/XML), Excel",
    trySample: "Try a sample",
    noFormats: "Select at least one output format to enable downloads.",
    uploadFirst: "Upload an SBOM file to enable preview and download.",
    pdfCancelled: "PDF save cancelled.",
    errFormat:
      "Make sure the file is an SBOM: SPDX (JSON/YAML/Tag-Value/RDF), CycloneDX (JSON/XML), or Excel.",
    errParse: "The file looks corrupted or incomplete. Try re-exporting the SBOM.",
    errTooLarge: "The file is over the 25 MB limit.",
    errEmpty: "The selected file is empty.",
    errEngine: "The local engine isn't responding. Please restart the app.",
    settings: "Settings",
    formats: "Output formats",
    organization: "Organization",
    contactEmail: "Contact email",
    sourceUrl: "Source code URL",
    preview: "Preview",
    download: "Download",
    generate: "Generate preview",
    components: "components",
    noFile: "No file selected yet.",
    parsing: "Parsing…",
    rendering: "Rendering…",
    error: "Error",
  },
} as const;

export type MessageKey = keyof (typeof messages)["en"];

export function t(lang: UiLang, key: MessageKey): string {
  return messages[lang][key];
}
