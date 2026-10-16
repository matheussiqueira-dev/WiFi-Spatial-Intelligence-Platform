import { expect, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import path from "node:path";
import AxeBuilder from "@axe-core/playwright";

test("official RuView: synthetic streaming, outage, reconnect, persistent history and source switch", async ({
  page,
  request,
}) => {
  test.skip(
    process.env.E2E_RUVIEW !== "1",
    "Run scripts/verify/check.ps1 -RuView for the official service.",
  );
  if (process.env.E2E_EXTERNAL === "1")
    throw new Error("RuView E2E requires its isolated native API/database.");
  const token = "e2e-only-" + "x".repeat(40);
  const base = "http://127.0.0.1:4810/api/v1";
  const auth = { Authorization: `Bearer ${token}` };
  const docker = (args: string[]) =>
    execFileSync("docker", args, {
      encoding: "utf8",
      cwd: path.resolve(__dirname, "../../.."),
    }).trim();
  const container = docker([
    "compose",
    "--env-file",
    "artifacts/ruview-verification.env",
    "-f",
    "compose.ruview.yaml",
    "-p",
    "wifi-spatial-f2-verification",
    "ps",
    "-q",
    "ruview",
  ]);
  expect(container).toMatch(/^[a-f0-9]{64}$/);
  expect(
    docker([
      "inspect",
      container,
      "--format",
      '{{index .Config.Labels "com.docker.compose.project"}}',
    ]),
  ).toBe("wifi-spatial-f2-verification");
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await request.post(`${base}/simulation/stop`, { headers: auth });
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  await page.getByLabel("Fonte de dados").selectOption("RUVIEW_STREAM");
  await expect(page.getByTestId("ruview-diagnostics")).toBeVisible();
  await expect(page.getByLabel("Cenário", { exact: true })).toHaveCount(0);
  const eventFrame = new Promise<void>((resolve) =>
    page.on("websocket", (ws) =>
      ws.on("framereceived", (f) => {
        if (f.payload.toString().includes('"ruview-01"')) resolve();
      }),
    ),
  );
  // Source selection does not reconnect the dashboard socket, so reload first.
  await page.reload();
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  await page.getByRole("button", { name: "Iniciar simulação" }).click();
  await eventFrame;
  await expect(page.getByTestId("ruview-diagnostics")).toContainText(
    "Recebendo fluxo",
  );
  await expect(page.locator("#history tbody tr").first()).toContainText(
    "RuView / simulated",
  );
  await expect(page.locator("#history tbody tr").first()).toContainText(
    "L0_SYNTHETIC",
  );
  await expect(page.getByTestId("occupant")).toHaveCount(0);
  await expect(page.getByTestId("virtual-sensor")).toHaveCount(0);
  await expect(page.getByLabel("Fonte de dados")).toBeDisabled();
  await page.getByRole("button", { name: "Pausar", exact: true }).click();
  const paused = (
    await (await request.get(`${base}/events`, { headers: auth })).json()
  ).total;
  await page.waitForTimeout(350);
  expect(
    (await (await request.get(`${base}/events`, { headers: auth })).json())
      .total,
  ).toBe(paused);
  await page.getByRole("button", { name: "Continuar", exact: true }).click();
  docker(["pause", container]);
  try {
    await expect(page.getByTestId("ruview-diagnostics")).toContainText(
      "Sem dados recentes",
      { timeout: 15000 },
    );
    await expect(page.getByTestId("ruview-diagnostics")).toContainText(
      "Reconectando",
    );
  } finally {
    docker(["unpause", container]);
  }
  await expect(page.getByTestId("ruview-diagnostics")).toContainText(
    "Recebendo fluxo",
    { timeout: 20000 },
  );
  await expect
    .poll(
      async () =>
        (
          await (
            await request.get(`${base}/system/status`, { headers: auth })
          ).json()
        ).source_diagnostics.reconnections,
    )
    .toBeGreaterThan(0);
  await page.getByRole("button", { name: "Parar", exact: true }).click();
  await expect(page.locator(".error")).toHaveCount(0);
  const saved = (
    await (await request.get(`${base}/events`, { headers: auth })).json()
  ).total;
  await page.reload();
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  await expect(
    page.getByText(`${saved} eventos persistidos localmente em SQLite`),
  ).toBeVisible();
  await expect(page.locator("#history tbody tr").first()).toContainText(
    "RuView / simulated",
  );
  await page.screenshot({
    path: "../../artifacts/ruview-dashboard-desktop.png",
    fullPage: true,
  });
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "../../artifacts/ruview-dashboard-mobile.png",
    fullPage: true,
  });
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await page.getByLabel("Fonte de dados").selectOption("synthetic-native");
  await page.getByLabel("Cenário", { exact: true }).selectOption("stationary");
  await page.getByRole("button", { name: "Iniciar simulação" }).click();
  await expect(page.getByTestId("occupant")).toHaveCount(2);
  await expect(page.getByTestId("virtual-sensor")).toHaveCount(6);
  await page.getByRole("button", { name: "Parar", exact: true }).click();
  expect(errors).toEqual([]);
});
