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
