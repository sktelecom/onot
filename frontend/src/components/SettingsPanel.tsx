// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import type { CompanyConfig } from "../lib/api";
import { t, type MessageKey, type UiLang } from "../lib/i18n";
import { Card, CardTitle } from "./ui/Card";

export interface NoticeSettings {
  formats: string[];
  lang: UiLang;
  company: CompanyConfig;
  remember: boolean;
}

const COMPANY_FIELDS = [
  { key: "organization", label: "organization", hint: "organizationHint", type: "text" },
  { key: "contact_email", label: "contactEmail", hint: "contactEmailHint", type: "email" },
  { key: "source_download_url", label: "sourceUrl", hint: "sourceUrlHint", type: "url" },
  { key: "copyright_holder", label: "copyrightHolder", hint: "copyrightHolderHint", type: "text" },
] as const satisfies readonly {
  key: keyof CompanyConfig;
  label: MessageKey;
  hint: MessageKey;
  type: string;
}[];

export function SettingsPanel({
  uiLang,
  value,
  onChange,
}: {
  uiLang: UiLang;
  value: NoticeSettings;
  onChange: (settings: NoticeSettings) => void;
}) {
  return (
    <Card>
      <CardTitle>{t(uiLang, "stepDetails")}</CardTitle>
      <p className="-mt-2 mb-3 text-xs text-fg-muted">{t(uiLang, "settingsHint")}</p>

      {COMPANY_FIELDS.map(({ key, label, hint, type }) => (
        <label key={key} className="mb-2 block text-sm">
          <span className="mb-1 block text-xs font-medium text-fg-muted">{t(uiLang, label)}</span>
          <input
            type={type}
            placeholder={t(uiLang, hint)}
            value={value.company[key] ?? ""}
            onChange={(e) =>
              onChange({ ...value, company: { ...value.company, [key]: e.target.value } })
            }
            className="w-full rounded-control border border-border-strong bg-transparent px-2 py-1.5 placeholder:text-fg-muted"
          />
        </label>
      ))}

      <label className="mt-3 flex items-center gap-1.5 text-xs text-fg-muted">
        <input
          type="checkbox"
          className="accent-brand"
          checked={value.remember}
          onChange={(e) => onChange({ ...value, remember: e.target.checked })}
        />
        {t(uiLang, "rememberDetails")}
      </label>
    </Card>
  );
}
