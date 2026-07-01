// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

// Lifecycle management for the Python FastAPI sidecar (pure Node — no electron dependency, unit-testable).
import { spawn } from "node:child_process";
import { closeSync, openSync } from "node:fs";
import http from "node:http";
import net from "node:net";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Spawn options for the sidecar. windowsHide prevents the console-subsystem sidecar exe from
// flashing a console window on Windows. When a log fd is given, stdout/stderr are captured so a
// failed startup (e.g. blocked by antivirus) leaves diagnostics instead of a silent exit.
export function spawnOptions(logFd = null) {
  return {
    stdio: logFd == null ? "ignore" : ["ignore", logFd, logFd],
    windowsHide: true,
  };
}

export function findFreePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.unref();
    srv.on("error", reject);
    srv.listen(0, "127.0.0.1", () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
  });
}

function ping(port) {
  return new Promise((resolve) => {
    const req = http.get({ host: "127.0.0.1", port, path: "/healthz", timeout: 1000 }, (res) => {
      res.resume();
      resolve(res.statusCode === 200);
    });
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

function waitExit(proc, ms) {
  return new Promise((resolve) => {
    if (proc.exitCode !== null) return resolve(true);
    const timer = setTimeout(() => resolve(false), ms);
    proc.once("exit", () => {
      clearTimeout(timer);
      resolve(true);
    });
  });
}

export class Sidecar {
  constructor({ command, args = [], port, logPath = null }) {
    this.command = command;
    this.args = args;
    this.port = port;
    this.logPath = logPath;
    this.logFd = null;
    this.proc = null;
  }

  async start({ timeoutMs = 30000 } = {}) {
    if (this.logPath) {
      try {
        this.logFd = openSync(this.logPath, "a");
      } catch {
        this.logFd = null; // logging is best-effort; never block startup on it
      }
    }
    this.proc = spawn(this.command, [...this.args, "--port", String(this.port)], spawnOptions(this.logFd));
    this.proc.once("exit", () => {
      this.proc = null;
      if (this.logFd !== null) {
        try {
          closeSync(this.logFd);
        } catch {
          /* already closed */
        }
        this.logFd = null;
      }
    });
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      if (this.proc === null) throw new Error("sidecar exited during startup");
      if (await ping(this.port)) return this.port;
      await sleep(250);
    }
    await this.stop();
    throw new Error(`sidecar did not become healthy within ${timeoutMs}ms`);
  }

  get pid() {
    return this.proc?.pid ?? null;
  }

  async healthy() {
    return ping(this.port);
  }

  // Graceful SIGTERM, then SIGKILL if it does not exit. Prevents orphan processes.
  async stop() {
    const proc = this.proc;
    if (!proc) return;
    proc.kill("SIGTERM");
    if (!(await waitExit(proc, 5000))) {
      proc.kill("SIGKILL");
      await waitExit(proc, 2000);
    }
    this.proc = null;
  }
}
