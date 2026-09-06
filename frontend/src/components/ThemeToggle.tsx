// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { Monitor, Moon, Sun } from "lucide-react";
import { useState } from "react";
import { cn } from "../lib/cn";
import { t, type MessageKey, type UiLang } from "../lib/i18n";
import { applyTheme, readPref, THEME_PREFS, type ThemePref, writePref } from "../lib/theme";

const ICONS: Record<ThemePref, typeof Monitor> = {
  system: Monitor,
  light: Sun,
  dark: Moon,
};

const LABELS: Record<ThemePref, MessageKey> = {
  system: "themeSystem",
  light: "themeLight",
  dark: "themeDark",
};

export function ThemeToggle({ lang }: { lang: UiLang }) {
  // "system" needs no listener: the stylesheet leaves color-scheme open and the OS drives it.
  const [pref, setPref] = useState<ThemePref>(() => readPref());

  function choose(next: ThemePref) {
    setPref(next);
    writePref(next);
    applyTheme(next);
  }

  return (
    <div
      role="group"
      aria-label={t(lang, "theme")}
      className="inline-flex rounded-control border border-border p-0.5"
    >
      {THEME_PREFS.map((value) => {
        const Icon = ICONS[value];
        const selected = pref === value;
        return (
          <button
            key={value}
            type="button"
            aria-pressed={selected}
            data-testid={`theme-${value}`}
            onClick={() => choose(value)}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-control px-2 py-1 text-xs font-medium transition",
              selected ? "bg-brand text-on-brand" : "text-fg-muted hover:bg-surface-sunken",
            )}
          >
            <Icon className="h-3.5 w-3.5" aria-hidden />
            {t(lang, LABELS[value])}
          </button>
        );
      })}
    </div>
  );
}
