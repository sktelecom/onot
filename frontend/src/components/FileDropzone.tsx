// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { FileText, UploadCloud, X } from "lucide-react";
import { useCallback, useId, useState } from "react";
import { cn } from "../lib/cn";
import { t, type UiLang } from "../lib/i18n";

export function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileDropzone({
  lang,
  onFile,
  file,
  onClear,
}: {
  lang: UiLang;
  onFile: (file: File) => void;
  file?: File | null;
  onClear?: () => void;
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
  // be drawn on the label instead, which is what the has-[…] variants below do. Remove sits
  // outside the label for the same reason: a button inside it would nest two controls.
  return (
    <div className="space-y-2">
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
          "flex cursor-pointer flex-col items-center justify-center gap-2 rounded-card border-2 border-dashed text-center transition",
          "has-[input:focus-visible]:outline-2 has-[input:focus-visible]:outline-offset-2 has-[input:focus-visible]:outline-accent",
          // Once a file is in, the drop target shrinks out of the way of the results below it.
          file ? "p-4" : "p-10",
          // The border is the only thing marking the drop target, so it has to clear the 3:1
          // non-text contrast bar on its own; the drag state also shifts the fill and the icon.
          over ? "border-brand bg-brand/10" : "border-border-strong",
        )}
      >
        {file ? (
          <span className="flex items-center gap-2 text-sm">
            <FileText className="h-4 w-4 shrink-0 text-fg-muted" aria-hidden />
            <span className="font-medium">{file.name}</span>
            <span className="text-fg-muted">{formatSize(file.size)}</span>
            <span className="text-xs text-accent underline">{t(lang, "replaceFile")}</span>
          </span>
        ) : (
          <>
            <UploadCloud
              className={cn("h-8 w-8", over ? "text-accent" : "text-fg-muted")}
              aria-hidden
            />
            <span className="text-sm font-medium">{t(lang, "dropzone")}</span>
            <span id={hintId} className="text-xs text-fg-muted">
              {t(lang, "dropzoneHint")}
            </span>
          </>
        )}
        <input
          type="file"
          // Hint the OS chooser toward SBOM types (drag-drop stays unrestricted).
          accept=".spdx,.json,.yaml,.yml,.xml,.rdf,.xlsx"
          aria-label={t(lang, "dropzone")}
          aria-describedby={file ? undefined : hintId}
          className="sr-only"
          data-testid="file-input"
          onChange={(e) => pick(e.target.files)}
        />
      </label>

      {file && onClear && (
        <button
          type="button"
          data-testid="clear-file"
          onClick={onClear}
          className="inline-flex items-center gap-1 rounded-control px-1 text-xs text-fg-muted hover:text-fg"
        >
          <X className="h-3.5 w-3.5" aria-hidden />
          {t(lang, "removeFile")}
        </button>
      )}
    </div>
  );
}
