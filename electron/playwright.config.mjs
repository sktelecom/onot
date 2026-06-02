import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  testMatch: "**/*.e2e.mjs",
  timeout: 120000,
  fullyParallel: false,
  workers: 1,
  reporter: "list",
});
