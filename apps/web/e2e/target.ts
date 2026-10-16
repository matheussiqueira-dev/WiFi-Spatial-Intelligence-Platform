import { execFileSync } from "node:child_process";

/** Compose projects created by scripts/verify/docker-e2e.ps1 (one per run). */
export const ISOLATED_PROJECT_PREFIX = "wifi-spatial-native-e2e";

export type E2ETarget = {
  external: boolean;
  token: string;
  apiBase: string;
};

/**
 * Local runner (API on 4810, temporary database) or an explicitly identified
 * isolated Compose stack. Specs stop sessions and delete history, so external
 * mode never falls back to the usage stack (port 8000, token from .env).
 */
export function e2eTarget(): E2ETarget {
  if (process.env.E2E_EXTERNAL !== "1") {
    return {
      external: false,
      token: "e2e-only-" + "x".repeat(40),
      apiBase: "http://127.0.0.1:4810/api/v1",
    };
  }
  const project = process.env.E2E_COMPOSE_PROJECT ?? "";
  const token = process.env.E2E_TOKEN ?? "";
  const port = Number(process.env.E2E_API_PORT);
  if (
    !project.startsWith(ISOLATED_PROJECT_PREFIX) ||
    token.length < 32 ||
    !Number.isInteger(port) ||
    port <= 0 ||
    port === 8000
  ) {
    throw new Error(
      "External E2E requires an isolated wifi-spatial-native-e2e* project with explicit E2E_TOKEN and E2E_API_PORT; run scripts/verify/docker-e2e.ps1.",
    );
  }
  // The published port must belong to that project's api container.
  const ports = execFileSync(
    "docker",
    [
      "ps",
      "--filter",
      `label=com.docker.compose.project=${project}`,
      "--filter",
      "label=com.docker.compose.service=api",
      "--format",
      "{{.Ports}}",
    ],
    { encoding: "utf8" },
  );
  if (!ports.includes(`127.0.0.1:${port}->8000/tcp`)) {
    throw new Error(
      `Port ${port} is not published by the api container of ${project}.`,
    );
  }
  return { external: true, token, apiBase: `http://127.0.0.1:${port}/api/v1` };
}
