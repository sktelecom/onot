// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// UI label catalog. Separate from the backend notice i18n (these are app-screen strings).
export type UiLang = "en";

export const messages = {
  en: {
    title: "OSS Notice Generator",
    subtitle: "Generate open source notices from SBOM documents, offline.",
    appName: "onot",

    starting: "Starting the local engine...",
    startingHint:
      "The first launch can take a minute while your antivirus scans the app. Nothing leaves this machine.",

    stepSbom: "1. SBOM",
    stepDetails: "2. Notice details",
    stepOutput: "3. Output",

    dropzone: "Drop an SBOM file here, or click to browse",
    dropzoneHint: "SPDX (JSON/YAML/Tag-Value/RDF), CycloneDX (JSON/XML), Excel",
    trySample: "Try a sample",
    replaceFile: "Replace",
    removeFile: "Remove",
    fileSelected: "{name} selected, {count} components found.",

    noFormats: "Select at least one output format to enable saving.",
    uploadFirst: "Upload an SBOM file to enable preview and saving.",
    pdfCancelled: "PDF save cancelled.",
    saveCancelled: "Save cancelled.",

    errFormat:
      "Make sure the file is an SBOM: SPDX (JSON/YAML/Tag-Value/RDF), CycloneDX (JSON/XML), or Excel.",
    errParse: "The file looks corrupted or incomplete. Try re-exporting the SBOM.",
    errTooLarge: "The file is over the 25 MB limit.",
    errEmpty: "The selected file is empty.",
    errEngine: "The local engine isn't responding. Please restart the app.",
    errRead: "Couldn't read that file.",

    settings: "Notice details",
    settingsHint: "Optional. These appear in the notice you generate.",
    formats: "Output formats",
    organization: "Organization",
    contactEmail: "Contact email",
    sourceUrl: "Source code URL",
    copyrightHolder: "Copyright holder",
    organizationHint: "Example Corp.",
    contactEmailHint: "compliance@example.com",
    sourceUrlHint: "https://github.com/your-org/your-product",
    copyrightHolderHint: "Defaults to the organization",
    rememberDetails: "Remember these details",

    preview: "Preview",
    previewNote: "The preview always shows the HTML notice.",
    expand: "Expand",
    collapse: "Collapse",

    save: "Save notice",
    saveOne: "Save notice ({format})",
    saveMany: "Save {count} notices",
    saving: "Saving...",
    savedTo: "Saved to {path}",
    savedCount: "Saved {count} notices to {dir}",
    showInFolder: "Show in folder",
    generate: "Preview",
    rendering: "Rendering...",

    components: "components",
    licenses: "licenses",
    warningCount: "{count} warnings",
    warningCountOne: "1 warning",
    show: "Show",
    hide: "Hide",
    warnNoLicense:
      "No license information: the notice lists this component without a license. Check the SBOM.",
    warnNoText:
      "No license text available offline: the notice names the license but cannot reproduce it. Try --online, or add the text yourself.",
    warnUnknown: "Unrecognized license identifier: the notice keeps it as written.",

    noFile: "No file selected yet.",
    parsing: "Parsing...",
    error: "Error",
    dismiss: "Dismiss",

    theme: "Theme",
    themeSystem: "System",
    themeLight: "Light",
    themeDark: "Dark",
  },
} as const;

export type MessageKey = keyof (typeof messages)["en"];

export function t(lang: UiLang, key: MessageKey): string {
  return messages[lang][key];
}

/** Same catalog, with {name} placeholders filled in. Mirrors the backend's message format. */
export function tf(
  lang: UiLang,
  key: MessageKey,
  vars: Record<string, string | number>,
): string {
  return t(lang, key).replace(/\{(\w+)\}/g, (match, name: string) =>
    name in vars ? String(vars[name]) : match,
  );
}
