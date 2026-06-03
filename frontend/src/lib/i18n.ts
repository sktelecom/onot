// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// UI 라벨 다국어. 백엔드 고지문 i18n과 별개(여기는 앱 화면 문구).
export type UiLang = "en" | "ko";

export const messages = {
  en: {
    title: "OSS Notice Generator",
    subtitle: "Generate open source notices from SBOM documents — offline.",
    dropzone: "Drop an SBOM file here, or click to browse",
    dropzoneHint: "SPDX (JSON/YAML/Tag-Value/RDF), CycloneDX (JSON/XML), Excel",
    settings: "Settings",
    formats: "Output formats",
    language: "Notice language",
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
  ko: {
    title: "오픈소스 고지문 생성기",
    subtitle: "SBOM 문서에서 오픈소스 고지문을 오프라인으로 생성합니다.",
    dropzone: "SBOM 파일을 여기에 끌어다 놓거나 클릭해 선택하세요",
    dropzoneHint: "SPDX(JSON/YAML/Tag-Value/RDF), CycloneDX(JSON/XML), Excel",
    settings: "설정",
    formats: "출력 포맷",
    language: "고지문 언어",
    organization: "조직명",
    contactEmail: "연락 이메일",
    sourceUrl: "소스 코드 URL",
    preview: "미리보기",
    download: "다운로드",
    generate: "미리보기 생성",
    components: "개 구성요소",
    noFile: "아직 선택된 파일이 없습니다.",
    parsing: "파싱 중…",
    rendering: "렌더링 중…",
    error: "오류",
  },
} as const;

export type MessageKey = keyof (typeof messages)["en"];

export function t(lang: UiLang, key: MessageKey): string {
  return messages[lang][key];
}
