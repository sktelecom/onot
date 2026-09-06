// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { Maximize2, Minimize2 } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "../lib/cn";
import { t, type UiLang } from "../lib/i18n";
import { Button } from "./ui/Button";
import { Card, CardTitle } from "./ui/Card";

/**
 * A blob URL, not srcdoc. An about:srcdoc document takes its base URL from the parent, so a
 * link to "#licenses" in the notice resolves against the app's own URL: clicking one in the
 * table of contents navigated the frame to the app and left the preview blank. A blob document
 * has a URL of its own, so the same link scrolls, exactly as it does in the saved file.
 */
function useObjectUrl(html: string): string {
  const [url, setUrl] = useState("");
  useEffect(() => {
    const objectUrl = URL.createObjectURL(new Blob([html], { type: "text/html" }));
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [html]);
  return url;
}

export function Preview({ lang, html }: { lang: UiLang; html: string }) {
  // A real notice runs to hundreds of components, which is more than a fixed pane can show. The
  // expanded height is tied to the viewport so it fills whatever window the reader has.
  const [expanded, setExpanded] = useState(false);
  const url = useObjectUrl(html);
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
      {/* The sandbox withholds allow-scripts, so nothing in the notice can execute: no script,
          no form, no navigation of the app around it. allow-same-origin is granted because a
          fully opaque origin also refuses the notice's own anchor links, which left the table
          of contents inert. The pairing to avoid is allow-same-origin with allow-scripts, where
          a frame can lift its own sandbox; with scripts off there is nothing to lift it with.
          The frame keeps a white page in both themes because a notice is a light document. */}
      <iframe
        title={title}
        src={url}
        sandbox="allow-same-origin"
        className={cn(
          "w-full rounded-control border border-border bg-white transition-[height]",
          expanded ? "h-[calc(100vh-12rem)]" : "h-[60vh]",
        )}
      />
      <p className="mt-2 text-xs text-fg-muted">{t(lang, "previewNote")}</p>
    </Card>
  );
}
