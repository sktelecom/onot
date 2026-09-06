// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { Download, Eye, Loader2 } from "lucide-react";
import { ALL_FORMATS, formatLabel } from "../lib/formats";
import { t, tf, type UiLang } from "../lib/i18n";
import type { NoticeSettings } from "./SettingsPanel";
import { Button } from "./ui/Button";
import { Card, CardTitle } from "./ui/Card";

export function OutputPanel({
  uiLang,
  value,
  onChange,
  onSave,
  onPreview,
  ready,
  saving,
  rendering,
}: {
  uiLang: UiLang;
  value: NoticeSettings;
  onChange: (settings: NoticeSettings) => void;
  onSave: () => void;
  onPreview: () => void;
  ready: boolean;
  saving: boolean;
  rendering: boolean;
}) {
  const toggleFormat = (fmt: string) => {
    const has = value.formats.includes(fmt);
    onChange({
      ...value,
      formats: has ? value.formats.filter((f) => f !== fmt) : [...value.formats, fmt],
    });
  };

  const count = value.formats.length;
  // Saving a file is the reason anyone opened this app, so it is the primary button. The
  // preview is a step on the way, and used to hold that position.
  const saveLabel =
    count === 1
      ? tf(uiLang, "saveOne", { format: formatLabel(value.formats[0]) })
      : tf(uiLang, "saveMany", { count });
  const canAct = ready && count > 0 && !saving && !rendering;

  return (
    <Card>
      <CardTitle>{t(uiLang, "stepOutput")}</CardTitle>

      <fieldset className="mb-4">
        <legend className="mb-1 text-xs font-medium text-fg-muted">{t(uiLang, "formats")}</legend>
        <div className="flex flex-wrap gap-3">
          {ALL_FORMATS.map(({ id, label }) => (
            <label key={id} className="flex items-center gap-1.5 text-sm">
              <input
                type="checkbox"
                // accent-color keeps the native control on the app's brand instead of the OS
                // default, which used to disagree with the app whenever the two themes differed.
                className="accent-brand"
                checked={value.formats.includes(id)}
                onChange={() => toggleFormat(id)}
              />
              {label}
            </label>
          ))}
        </div>
      </fieldset>

      <div className="flex flex-col gap-2">
        <Button data-testid="save-notice" onClick={onSave} disabled={!canAct} aria-busy={saving}>
          {saving ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          ) : (
            <Download className="h-4 w-4" aria-hidden />
          )}
          {saving ? t(uiLang, "saving") : saveLabel}
        </Button>
        <Button
          variant="secondary"
          data-testid="generate-preview"
          onClick={onPreview}
          disabled={!ready || saving || rendering}
          aria-busy={rendering}
        >
          {rendering ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          ) : (
            <Eye className="h-4 w-4" aria-hidden />
          )}
          {rendering ? t(uiLang, "rendering") : t(uiLang, "generate")}
        </Button>

        {count === 0 && <p className="text-xs text-fg-muted">{t(uiLang, "noFormats")}</p>}
        {!ready && <p className="text-xs text-fg-muted">{t(uiLang, "uploadFirst")}</p>}
      </div>
    </Card>
  );
}
