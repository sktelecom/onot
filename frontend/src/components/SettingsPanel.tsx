// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import type { CompanyConfig } from "../lib/api";
import { t, type UiLang } from "../lib/i18n";
import { Card, CardTitle } from "./ui/Card";

export interface NoticeSettings {
  formats: string[];
  lang: UiLang;
  company: CompanyConfig;
}

const ALL_FORMATS = ["html", "text", "markdown", "pdf"];

const COMPANY_FIELDS = [
  { key: "organization", label: "organization" },
  { key: "contact_email", label: "contactEmail" },
  { key: "source_download_url", label: "sourceUrl" },
] as const;

export function SettingsPanel({
  uiLang,
  value,
  onChange,
}: {
  uiLang: UiLang;
  value: NoticeSettings;
  onChange: (settings: NoticeSettings) => void;
}) {
  const toggleFormat = (fmt: string) => {
    const has = value.formats.includes(fmt);
    onChange({
      ...value,
      formats: has ? value.formats.filter((f) => f !== fmt) : [...value.formats, fmt],
    });
  };

  return (
    <Card>
      <CardTitle>{t(uiLang, "settings")}</CardTitle>

      <fieldset className="mb-4">
        <legend className="mb-1 text-xs font-medium text-zinc-500">{t(uiLang, "formats")}</legend>
        <div className="flex flex-wrap gap-3">
          {ALL_FORMATS.map((fmt) => (
            <label key={fmt} className="flex items-center gap-1.5 text-sm">
              <input
                type="checkbox"
                checked={value.formats.includes(fmt)}
                onChange={() => toggleFormat(fmt)}
              />
              {fmt}
            </label>
          ))}
        </div>
      </fieldset>

      <label className="mb-3 block text-sm">
        <span className="mb-1 block text-xs font-medium text-zinc-500">
          {t(uiLang, "language")}
        </span>
        <select
          value={value.lang}
          onChange={(e) => onChange({ ...value, lang: e.target.value as UiLang })}
          className="w-full rounded-md border border-zinc-300 bg-transparent px-2 py-1.5 dark:border-zinc-700"
        >
          <option value="en">English</option>
          <option value="ko">한국어</option>
        </select>
      </label>

      {COMPANY_FIELDS.map(({ key, label }) => (
        <label key={key} className="mb-2 block text-sm">
          <span className="mb-1 block text-xs font-medium text-zinc-500">{t(uiLang, label)}</span>
          <input
            value={value.company[key] ?? ""}
            onChange={(e) =>
              onChange({ ...value, company: { ...value.company, [key]: e.target.value } })
            }
            className="w-full rounded-md border border-zinc-300 bg-transparent px-2 py-1.5 dark:border-zinc-700"
          />
        </label>
      ))}
    </Card>
  );
}
