import { spawnSync } from "node:child_process";

if (!process.env.npm_execpath)
  throw new Error("Run this script through npm run build:e2e.");
const result = spawnSync(
  process.execPath,
  [process.env.npm_execpath, "run", "build"],
  {
    stdio: "inherit",
    env: {
      ...process.env,
      NEXT_PUBLIC_API_URL: "http://127.0.0.1:4810",
      NEXT_TELEMETRY_DISABLED: "1",
    },
  },
);
process.exit(result.status ?? 1);
