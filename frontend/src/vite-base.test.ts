// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Regression guard for the packaged-app blank screen (issue #68).
// The Electron production build loads the renderer over file:// (loadFile). With Vite's
// default base "/", assets are emitted as absolute paths ("/assets/...") that resolve to the
// drive root under file:// and never load, leaving a blank window. base "./" keeps them relative.
// Read the config as raw text (importing it pulls in esbuild, which cannot load under jsdom).
import { expect, test } from "vitest";
import configSource from "../vite.config.ts?raw";

test('vite base is "./" so packaged assets load over file:// (issue #68)', () => {
  expect(configSource).toMatch(/base:\s*["']\.\/["']/);
});
