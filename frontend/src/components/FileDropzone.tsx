// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { UploadCloud } from "lucide-react";
import { useCallback, useState } from "react";
import { cn } from "../lib/cn";
import { t, type UiLang } from "../lib/i18n";

export function FileDropzone({
  lang,
  onFile,
  fileName,
}: {
  lang: UiLang;
  onFile: (file: File) => void;
  fileName?: string;
}) {
  const [over, setOver] = useState(false);

  const pick = useCallback(
    (files: FileList | null) => {
      if (files && files[0]) onFile(files[0]);
    },
    [onFile],
  );

  // Accessibility: the <label> delegates click/focus to the input, and the input is sr-only
  // (still focusable) to support keyboard activation. No nested role=button, so no
  // nested-interactive violation.
  return (
    <label
      data-testid="dropzone"
      onDragOver={(e) => {
        e.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setOver(false);
        pick(e.dataTransfer.files);
      }}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-10 text-center transition",
        over ? "border-brand bg-brand/5" : "border-zinc-300 dark:border-zinc-700",
      )}
    >
      <UploadCloud className="h-8 w-8 text-zinc-400" aria-hidden />
      <p className="text-sm font-medium">{fileName ?? t(lang, "dropzone")}</p>
      <p className="text-xs text-zinc-400">{t(lang, "dropzoneHint")}</p>
      <input
        type="file"
        // Hint the OS chooser toward SBOM types (drag-drop stays unrestricted).
        accept=".spdx,.json,.yaml,.yml,.xml,.rdf,.xlsx"
        aria-label={t(lang, "dropzone")}
        className="sr-only"
        data-testid="file-input"
        onChange={(e) => pick(e.target.files)}
      />
    </label>
  );
}
