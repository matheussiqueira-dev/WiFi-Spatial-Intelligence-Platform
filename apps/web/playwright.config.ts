import { defineConfig, devices } from "@playwright/test";
import path from "node:path";
import os from "node:os";
import { randomUUID } from "node:crypto";

const root = path.resolve(__dirname, "../..");
const token = "e2e-only-" + "x".repeat(40);
const database = path
  .join(os.tmpdir(), `spatial-e2e-${randomUUID()}.db`)
  .replaceAll("\\", "/");
const external = process.env.E2E_EXTERNAL === "1";
const webPort = external ? Number(process.env.E2E_WEB_PORT ?? 3000) : 4310;
const apiPort = external ? Number(process.env.E2E_API_PORT ?? 8000) : 4810;
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 45000,
  expect: { timeout: 10000 },
  retries: 0,
  use: {
    baseURL: `http://127.0.0.1:${webPort}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: (process.env.E2E_BROWSERS ?? "chromium").split(",").map((name) => {
    const profiles: Record<string, string> = {
      chromium: "Desktop Chrome",
      firefox: "Desktop Firefox",
      webkit: "Desktop Safari",
    };
    if (!profiles[name]) throw new Error(`Unsupported E2E browser: ${name}`);
    return { name, use: { ...devices[profiles[name]] } };
  }),
  webServer: external
    ? undefined
    : [
        {
          command: `"${path.join(root, process.platform === "win32" ? "apps/api/.venv/Scripts/python.exe" : "apps/api/.venv/bin/python")}" -m uvicorn app.main:create_app --factory --app-dir apps/api --host 127.0.0.1 --port ${apiPort} --ws-max-size 4096 --ws-max-queue 16 --no-proxy-headers`,
          cwd: root,
          url: `http://127.0.0.1:${apiPort}/api/v1/health`,
          reuseExistingServer: false,
          env: {
            SPATIAL_TOKEN: token,
            SPATIAL_DATABASE_URL: `sqlite:///${database}`,
            SPATIAL_ORIGINS: JSON.stringify([`http://127.0.0.1:${webPort}`]),
            SPATIAL_RUVIEW_HTTP_URL:
              process.env.E2E_RUVIEW_HTTP_URL ?? "http://127.0.0.1:4860",
            SPATIAL_RUVIEW_WS_URL:
              process.env.E2E_RUVIEW_WS_URL ?? "ws://127.0.0.1:4861/ws/sensing",
            SPATIAL_RUVIEW_TOKEN: process.env.SPATIAL_RUVIEW_TOKEN ?? "",
            SPATIAL_RUVIEW_STALE_SECONDS: "2",
            SPATIAL_LEGACY_LAB_ENABLED:
              process.env.E2E_RUVIEW === "1" ? "true" : "false",
          },
        },
        {
          command: `"${process.execPath}" "${path.join(root, "node_modules/next/dist/bin/next")}" start --hostname 127.0.0.1 --port ${webPort}`,
          cwd: path.join(root, "apps/web"),
          url: `http://127.0.0.1:${webPort}/dashboard`,
          reuseExistingServer: false,
          env: { NEXT_TELEMETRY_DISABLED: "1" },
          timeout: 90000,
        },
      ],
});
