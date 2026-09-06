// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { Maximize2, Minimize2 } from "lucide-react";
import { useState } from "react";
import { cn } from "../lib/cn";
import { t, type UiLang } from "../lib/i18n";
import { Button } from "./ui/Button";
import { Card, CardTitle } from "./ui/Card";

export function Preview({ lang, html }: { lang: UiLang; html: string }) {
  // A real notice runs to hundreds of components, which is more than a fixed pane can show. The
  // expanded height is tied to the viewport so it fills whatever window the reader has.
  const [expanded, setExpanded] = useState(false);
  const title = t(lang, "preview");

  return (
    <Card>
      <div className="mb-3 flex items-center justify-between gap-3">
        <CardTitle className="mb-0">{title}</CardTitle>
        <Button
          variant="ghost"
          data-testid="toggle-preview-size"
          aria-expanded={expanded}
          onClick={() => setExpanded((value) => !value)}
          className="px-2 py-1 text-xs"
        >
          {expanded ? (
            <Minimize2 className="h-3.5 w-3.5" aria-hidden />
          ) : (
            <Maximize2 className="h-3.5 w-3.5" aria-hidden />
          )}
          {expanded ? t(lang, "collapse") : t(lang, "expand")}
        </Button>
      </div>
      {/* Isolate the preview with iframe srcdoc + sandbox (prevents CSS conflicts/blocks scripts).
          The frame keeps a white page in both themes because the notice is a light document. */}
      <iframe
        title={title}
        srcDoc={html}
        sandbox=""
        className={cn(
          "w-full rounded-control border border-border bg-white transition-[height]",
          expanded ? "h-[calc(100vh-12rem)]" : "h-[60vh]",
        )}
      />
      <p className="mt-2 text-xs text-fg-muted">{t(lang, "previewNote")}</p>
    </Card>
  );
}
