// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { UploadCloud } from "lucide-react";
import { useCallback, useId, useState } from "react";
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
  const hintId = useId();

  const pick = useCallback(
    (files: FileList | null) => {
      if (files && files[0]) onFile(files[0]);
    },
    [onFile],
  );

  // Accessibility: the <label> delegates click/focus to the input, and the input is sr-only
  // (still focusable) to support keyboard activation. No nested role=button, so no
  // nested-interactive violation. Because the input itself is invisible, the focus ring has to
  // be drawn on the label instead, which is what the has-[…] variants below do.
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
        "flex cursor-pointer flex-col items-center justify-center gap-2 rounded-card border-2 border-dashed p-10 text-center transition",
        "has-[input:focus-visible]:outline-2 has-[input:focus-visible]:outline-offset-2 has-[input:focus-visible]:outline-accent",
        // The border is the only thing marking the drop target, so it has to clear the 3:1
        // non-text contrast bar on its own; the drag state also shifts the fill and the icon.
        over ? "border-brand bg-brand/10" : "border-border-strong",
      )}
    >
      <UploadCloud
        className={cn("h-8 w-8", over ? "text-accent" : "text-fg-muted")}
        aria-hidden
      />
      <p className="text-sm font-medium">{fileName ?? t(lang, "dropzone")}</p>
      <p id={hintId} className="text-xs text-fg-muted">
        {t(lang, "dropzoneHint")}
      </p>
      <input
        type="file"
        // Hint the OS chooser toward SBOM types (drag-drop stays unrestricted).
        accept=".spdx,.json,.yaml,.yml,.xml,.rdf,.xlsx"
        aria-label={t(lang, "dropzone")}
        aria-describedby={hintId}
        className="sr-only"
        data-testid="file-input"
        onChange={(e) => pick(e.target.files)}
      />
    </label>
  );
}
