// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Remember the window's size, position and maximised state between runs, and refuse to restore
// bounds that would land off-screen (an external monitor unplugged since the last run).
import fs from "node:fs";
import path from "node:path";

export const DEFAULT_BOUNDS = { width: 1200, height: 860 };
export const MIN_SIZE = { width: 900, height: 640 };

const FILE_NAME = "window-state.json";

function isFinitePair(a, b) {
  return Number.isFinite(a) && Number.isFinite(b);
}

/** True when enough of the window overlaps a work area to be grabbable. */
export function isOnScreen(bounds, workAreas) {
  if (!isFinitePair(bounds.x, bounds.y)) return false;
  const MIN_VISIBLE = 80;
  return workAreas.some((area) => {
    const overlapX = Math.min(bounds.x + bounds.width, area.x + area.width) - Math.max(bounds.x, area.x);
    const overlapY = Math.min(bounds.y + bounds.height, area.y + area.height) - Math.max(bounds.y, area.y);
    return overlapX >= MIN_VISIBLE && overlapY >= MIN_VISIBLE;
  });
}

/** Clamp a stored record to something usable, dropping anything malformed. */
export function sanitize(stored, workAreas) {
  const state = { ...DEFAULT_BOUNDS, maximized: false };
  if (!stored || typeof stored !== "object") return state;

  if (isFinitePair(stored.width, stored.height)) {
    state.width = Math.max(MIN_SIZE.width, Math.round(stored.width));
    state.height = Math.max(MIN_SIZE.height, Math.round(stored.height));
  }
  state.maximized = stored.maximized === true;

  const candidate = { x: stored.x, y: stored.y, width: state.width, height: state.height };
  if (isOnScreen(candidate, workAreas)) {
    state.x = Math.round(stored.x);
    state.y = Math.round(stored.y);
  }
  return state;
}

export function createWindowState({ userDataDir, workAreas }) {
  const file = path.join(userDataDir, FILE_NAME);

  let stored = null;
  try {
    stored = JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    // No state yet, or it is unreadable or corrupt: fall back to the defaults.
  }
  const state = sanitize(stored, workAreas);

  let saveTimer = null;
  function persist(window) {
    if (window.isDestroyed()) return;
    // Normal bounds, so a maximised or full-screen window still remembers where to return to.
    const bounds = window.getNormalBounds();
    const next = { ...bounds, maximized: window.isMaximized() };
    try {
      fs.writeFileSync(file, JSON.stringify(next));
    } catch {
      // Losing the window position is not worth surfacing to the user.
    }
  }

  return {
    bounds: state,
    /** Persist on the events that change geometry, coalesced so a drag writes once. */
    track(window) {
      const schedule = () => {
        clearTimeout(saveTimer);
        saveTimer = setTimeout(() => persist(window), 400);
      };
      for (const event of ["resize", "move", "maximize", "unmaximize"]) {
        window.on(event, schedule);
      }
      window.on("close", () => {
        clearTimeout(saveTimer);
        persist(window);
      });
    },
  };
}
