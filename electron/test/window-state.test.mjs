// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import assert from "node:assert/strict";
import test from "node:test";
import { DEFAULT_BOUNDS, isOnScreen, MIN_SIZE, sanitize } from "../lib/window-state.mjs";

const LAPTOP = [{ x: 0, y: 0, width: 1440, height: 900 }];
const TWO_SCREENS = [...LAPTOP, { x: 1440, y: 0, width: 1920, height: 1080 }];

test("falls back to the defaults with nothing stored", () => {
  assert.deepEqual(sanitize(null, LAPTOP), { ...DEFAULT_BOUNDS, maximized: false });
  assert.deepEqual(sanitize("garbage", LAPTOP), { ...DEFAULT_BOUNDS, maximized: false });
});

test("restores a size and position that fit the screen", () => {
  const state = sanitize({ x: 100, y: 80, width: 1000, height: 700 }, LAPTOP);
  assert.deepEqual(state, { x: 100, y: 80, width: 1000, height: 700, maximized: false });
});

test("never restores a window smaller than it can be dragged back from", () => {
  const state = sanitize({ x: 0, y: 0, width: 200, height: 120 }, LAPTOP);
  assert.equal(state.width, MIN_SIZE.width);
  assert.equal(state.height, MIN_SIZE.height);
});

test("drops a position from a screen that is no longer attached", () => {
  const onSecond = { x: 2000, y: 100, width: 1000, height: 700 };
  assert.equal(isOnScreen(onSecond, TWO_SCREENS), true);
  assert.equal(isOnScreen(onSecond, LAPTOP), false);

  // The size is still worth keeping; only the off-screen position is discarded.
  const state = sanitize(onSecond, LAPTOP);
  assert.equal(state.x, undefined);
  assert.equal(state.y, undefined);
  assert.equal(state.width, 1000);
});

test("treats a window with only a sliver on screen as off screen", () => {
  const barelyVisible = { x: 1400, y: 860, width: 1000, height: 700 };
  assert.equal(isOnScreen(barelyVisible, LAPTOP), false);
});

test("remembers the maximised state only when it was set", () => {
  assert.equal(sanitize({ maximized: true }, LAPTOP).maximized, true);
  assert.equal(sanitize({ maximized: "yes" }, LAPTOP).maximized, false);
  assert.equal(sanitize({}, LAPTOP).maximized, false);
});
