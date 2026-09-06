// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Optional persistence for the notice details. Someone generating notices for the same product
// every release should not retype their organisation each time, but these fields end up in a
// published document, so keeping them is opt-in rather than automatic.
import type { CompanyConfig } from "./api";

const COMPANY_KEY = "onot.company";
const REMEMBER_KEY = "onot.rememberCompany";

const FIELDS = [
  "organization",
  "contact_email",
  "copyright_holder",
  "source_download_url",
] as const;

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Storage is a convenience here; the values still apply for this session.
  }
}

function remove(key: string): void {
  try {
    localStorage.removeItem(key);
  } catch {
    // Nothing to do: the values were never stored.
  }
}

export function readRemember(): boolean {
  return read(REMEMBER_KEY) === "true";
}

/** Only the known fields are kept, so a hand-edited or stale entry cannot inject anything. */
export function readCompany(): CompanyConfig {
  const raw = read(COMPANY_KEY);
  if (!raw) return {};
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return {};
    const source = parsed as Record<string, unknown>;
    const company: CompanyConfig = {};
    for (const field of FIELDS) {
      const value = source[field];
      if (typeof value === "string" && value) company[field] = value;
    }
    return company;
  } catch {
    return {};
  }
}

export function saveCompany(company: CompanyConfig, remember: boolean): void {
  write(REMEMBER_KEY, String(remember));
  if (remember) {
    write(COMPANY_KEY, JSON.stringify(company));
  } else {
    remove(COMPANY_KEY);
  }
}
