// Python FastAPI 사이드카 수명주기 관리(순수 Node — electron 비의존, 단위 테스트 가능).
import { spawn } from "node:child_process";
import http from "node:http";
import net from "node:net";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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
  constructor({ command, args = [], port }) {
    this.command = command;
    this.args = args;
    this.port = port;
    this.proc = null;
  }

  async start({ timeoutMs = 30000 } = {}) {
    this.proc = spawn(this.command, [...this.args, "--port", String(this.port)], {
      stdio: "ignore",
    });
    this.proc.once("exit", () => {
      this.proc = null;
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

  // graceful SIGTERM 후 미종료 시 SIGKILL. 고아 프로세스 방지.
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
