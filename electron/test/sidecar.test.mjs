// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Sidecar lifecycle test (S4 regression): spawn→health→stop→no orphan.
// Verified by launching the real venv sidecar (python -m onot.api.serve) (electron not required).
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { tmpdir } from "node:os";
import net from "node:net";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { after, test } from "node:test";
import { findFreePort, Sidecar, spawnOptions } from "../lib/sidecar.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "..", "..");
const venvPython =
  process.env.ONOT_SIDECAR_PYTHON ?? path.join(repoRoot, ".venv", "bin", "python");

function isAlive(pid) {
  if (pid === null) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

let active;
after(async () => {
  if (active) await active.stop();
});

test("starts, reports healthy, then stops cleanly with no orphan", async () => {
  const port = await findFreePort();
  const sidecar = new Sidecar({ command: venvPython, args: ["-m", "onot.api.serve"], port });
  active = sidecar;

  await sidecar.start({ timeoutMs: 40000 });
  const pid = sidecar.pid;
  assert.ok(pid, "should have a pid after start");
  assert.equal(await sidecar.healthy(), true, "should be healthy");

  await sidecar.stop();
  assert.equal(sidecar.pid, null, "pid cleared after stop");

  // No orphan process should remain after shutdown (serve.py is single-process — no workers/reloader)
  await new Promise((r) => setTimeout(r, 500));
  assert.equal(isAlive(pid), false, "sidecar process must not survive stop()");
});

test("spawnOptions hides the console window and captures logs when given an fd (P1/P2)", () => {
  const noLog = spawnOptions(null);
  assert.equal(noLog.windowsHide, true, "windowsHide must be set so no console flashes on Windows");
  assert.equal(noLog.stdio, "ignore");

  const withLog = spawnOptions(7);
  assert.equal(withLog.windowsHide, true);
  assert.deepEqual(withLog.stdio, ["ignore", 7, 7], "stdout/stderr routed to the log fd");
});

test("logPath sidecar starts healthy and creates the log file (P2)", async () => {
  const port = await findFreePort();
  const logPath = path.join(tmpdir(), `onot-sidecar-test-${port}.log`);
  const sidecar = new Sidecar({
    command: venvPython,
    args: ["-m", "onot.api.serve"],
    port,
    logPath,
  });
  active = sidecar;
  await sidecar.start({ timeoutMs: 40000 });
  assert.equal(await sidecar.healthy(), true);
  assert.ok(existsSync(logPath), "sidecar log file should be created when logPath is set");
  await sidecar.stop();
});

test("findFreePort returns a port that is actually bindable", async () => {
  const port = await findFreePort();
  assert.ok(port > 0 && port < 65536);
  await new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.once("error", reject);
    srv.listen(port, "127.0.0.1", () => srv.close(resolve));
  });
});
