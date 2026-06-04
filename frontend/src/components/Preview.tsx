// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

export function Preview({ html, title }: { html: string; title: string }) {
  // Isolate the preview with iframe srcdoc + sandbox (prevents CSS conflicts/blocks scripts)
  return (
    <iframe
      title={title}
      srcDoc={html}
      sandbox=""
      className="h-[60vh] w-full rounded-lg border border-zinc-200 bg-white dark:border-zinc-800"
    />
  );
}
