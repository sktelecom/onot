// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import "@testing-library/jest-dom/vitest";

// This environment exposes no localStorage: Node's own implementation is off without
// --localstorage-file, and it shadows the one jsdom would otherwise provide. The app treats
// storage as optional and keeps working without it, but the theme tests need somewhere to
// persist a preference, so stand up a minimal in-memory Storage.
if (!globalThis.localStorage) {
  const store = new Map<string, string>();
  const storage: Storage = {
    get length() {
      return store.size;
    },
    clear: () => store.clear(),
    getItem: (key) => store.get(key) ?? null,
    key: (index) => [...store.keys()][index] ?? null,
    removeItem: (key) => void store.delete(key),
    setItem: (key, value) => void store.set(key, String(value)),
  };
  Object.defineProperty(globalThis, "localStorage", { value: storage, configurable: true });
}
