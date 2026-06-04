// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Sidecar lifecycle test (S4 regression): spawn→health→stop→no orphan.
// Verified by launching the real venv sidecar (python -m onot.api.serve) (electron not required).
import assert from "node:assert/strict";
import net from "node:net";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { after, test } from "node:test";
import { findFreePort, Sidecar } from "../lib/sidecar.mjs";

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

test("findFreePort returns a port that is actually bindable", async () => {
  const port = await findFreePort();
  assert.ok(port > 0 && port < 65536);
  await new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.once("error", reject);
    srv.listen(port, "127.0.0.1", () => srv.close(resolve));
  });
});
