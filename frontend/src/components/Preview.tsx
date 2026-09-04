// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

export function Preview({ html, title }: { html: string; title: string }) {
  // Isolate the preview with iframe srcdoc + sandbox (prevents CSS conflicts/blocks scripts).
  // The frame keeps a white page in both themes because the notice is a light document; theming
  // the generated notice itself is a separate decision from theming the app.
  return (
    <iframe
      title={title}
      srcDoc={html}
      sandbox=""
      className="h-[60vh] w-full rounded-control border border-border bg-white"
    />
  );
}
