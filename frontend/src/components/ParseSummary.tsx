// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { AlertTriangle, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";
import type { ParseResult } from "../lib/api";
import { t, tf, type MessageKey, type UiLang } from "../lib/i18n";
import { Card, CardTitle } from "./ui/Card";

// Backend warnings are written for a log, not for a reviewer. Each one gets a line saying what
// it means for the notice they are about to ship. Anything unrecognised is shown as-is.
function explain(warning: string): MessageKey | null {
  if (/^no license information for /i.test(warning)) return "warnNoLicense";
  if (/^missing license text for /i.test(warning)) return "warnNoText";
  if (/^unparseable expression for /i.test(warning)) return "warnUnknown";
  return null;
}

function expressionOf(pkg: ParseResult["document"]["packages"][number]): string {
  return pkg.license_concluded?.raw ?? pkg.license_declared?.raw ?? "";
}

/**
 * Packages per license id. Expressions can combine ids (AND/OR/WITH), so a package counts
 * towards every license it names, matched on a whole token the way the notice's own links are.
 */
export function licenseCounts(parsed: ParseResult): { id: string; count: number }[] {
  return parsed.document.licenses
    .map((license) => {
      const token = license.license_id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const pattern = new RegExp(`(^|[^\\w.-])${token}([^\\w.-]|$)`);
      const count = parsed.document.packages.filter((pkg) =>
        pattern.test(expressionOf(pkg)),
      ).length;
      return { id: license.license_id, count };
    })
    .sort((a, b) => b.count - a.count || a.id.localeCompare(b.id));
}

export function ParseSummary({ lang, parsed }: { lang: UiLang; parsed: ParseResult }) {
  const [open, setOpen] = useState(false);
  const counts = licenseCounts(parsed);
  const warnings = parsed.warnings;

  return (
    <Card>
      <CardTitle>{parsed.document.name}</CardTitle>
      <p className="text-sm text-fg-muted">
        {parsed.document.packages.length} {t(lang, "components")}, {parsed.document.licenses.length}{" "}
        {t(lang, "licenses")}
      </p>

      {counts.length > 0 && (
        <ul className="mt-3 flex flex-wrap gap-1.5">
          {counts.map(({ id, count }) => (
            <li
              key={id}
              className="rounded-control bg-surface-sunken px-2 py-0.5 text-xs text-fg-muted"
            >
              {id} <span className="font-medium text-fg">{count}</span>
            </li>
          ))}
        </ul>
      )}

      {warnings.length > 0 && (
        <div className="mt-3">
          <button
            type="button"
            data-testid="toggle-warnings"
            aria-expanded={open}
            onClick={() => setOpen((value) => !value)}
            className="inline-flex items-center gap-1.5 rounded-control text-xs font-medium text-warning-fg"
          >
            {open ? (
              <ChevronDown className="h-3.5 w-3.5" aria-hidden />
            ) : (
              <ChevronRight className="h-3.5 w-3.5" aria-hidden />
            )}
            <AlertTriangle className="h-3.5 w-3.5" aria-hidden />
            {warnings.length === 1
              ? t(lang, "warningCountOne")
              : tf(lang, "warningCount", { count: warnings.length })}
            <span className="text-fg-muted">{open ? t(lang, "hide") : t(lang, "show")}</span>
          </button>

          {open && (
            <ul className="mt-2 space-y-2">
              {warnings.map((warning) => {
                const key = explain(warning);
                return (
                  <li key={warning} className="text-xs">
                    <p className="font-mono text-fg-muted">{warning}</p>
                    {key && <p className="mt-0.5 text-warning-fg">{t(lang, key)}</p>}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
    </Card>
  );
}
