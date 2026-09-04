// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Theme preference. "system" is the absence of an override: the stylesheet leaves color-scheme
// as "light dark" and every light-dark() token follows the OS on its own, so nothing has to run
// before first paint. An explicit choice writes data-theme, which pins color-scheme instead.

export type ThemePref = "system" | "light" | "dark";

export const THEME_PREFS: readonly ThemePref[] = ["system", "light", "dark"] as const;

const STORAGE_KEY = "onot.theme";

function isPref(value: unknown): value is ThemePref {
  return value === "system" || value === "light" || value === "dark";
}

export function readPref(): ThemePref {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (isPref(stored)) return stored;
  } catch {
    // Private mode or a blocked storage partition: fall through to the default.
  }
  return "system";
}

export function writePref(pref: ThemePref): void {
  try {
    localStorage.setItem(STORAGE_KEY, pref);
  } catch {
    // Storage is a convenience here; the theme still applies for this session.
  }
}

export function applyTheme(pref: ThemePref): void {
  if (pref === "system") {
    delete document.documentElement.dataset.theme;
  } else {
    document.documentElement.dataset.theme = pref;
  }
}

/** Apply the stored override, if any. Called once at startup, before React renders. */
export function initTheme(): void {
  applyTheme(readPref());
}
