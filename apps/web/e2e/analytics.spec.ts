import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("analytics: persisted aggregates, replay, export and saved report", async ({
  page,
  request,
}) => {
  const external = process.env.E2E_EXTERNAL === "1";
  if (external && process.env.E2E_COMPOSE_PROJECT !== "wifi-spatial-native-e2e")
    throw new Error(
      "Analytics external E2E requires its isolated native stack.",
    );
  const token = process.env.E2E_TOKEN ?? "e2e-only-" + "x".repeat(40);
  const base = `http://127.0.0.1:${external ? Number(process.env.E2E_API_PORT ?? 8000) : 4810}/api/v1`;
  const headers = { Authorization: `Bearer ${token}` };
  await request.post(`${base}/simulation/stop`, { headers });
  await request.post(`${base}/sources/select`, {
    headers,
    data: { source: "SIMULATED" },
  });
  const started = await request.post(`${base}/simulation/start`, {
    headers,
    data: { scenario: "entering", occupants: 3, speed: 4 },
  });
  expect(started.ok()).toBe(true);
  await expect
    .poll(
      async () =>
        (await (await request.get(`${base}/system/status`, { headers })).json())
          .produced_events,
    )
    .toBeGreaterThanOrEqual(12);
  await request.post(`${base}/simulation/stop`, { headers });
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  const panel = page.locator("#analytics");
  await panel.getByLabel("Proveniência / cenário").selectOption("entering");
  await panel.getByRole("button", { name: "Consultar histórico" }).click();
  await expect(panel.getByTestId("analytics-samples")).toContainText(
    "observações históricas",
  );
  await expect(
    panel.getByText("Nenhuma observação no intervalo selecionado."),
  ).toHaveCount(0);
  await expect(panel.getByLabel("Posição no replay")).toBeVisible();
  const first = await panel.getByTestId("replay-time").textContent();
  await panel.getByRole("button", { name: "Reproduzir histórico" }).click();
  await expect(panel.getByTestId("replay-time")).not.toHaveText(first ?? "");
  await panel.getByRole("button", { name: "Pausar replay" }).click();
  await panel.getByLabel("Posição no replay").fill("0");
  await expect(panel.getByTestId("replay-time")).toHaveText(first ?? "");
  const jsonDownload = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Exportar JSON" }).click();
  expect((await jsonDownload).suggestedFilename()).toBe(
    "synthetic-analytics.json",
  );
  const csvDownload = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Exportar CSV" }).click();
  expect((await csvDownload).suggestedFilename()).toBe(
    "synthetic-analytics.csv",
  );
  await panel.getByRole("button", { name: "Salvar relatório" }).click();
  await expect(
    panel.getByRole("status", { name: "Resultado das análises" }),
  ).toContainText("salvo no SQLite");
  const reports = await (
    await request.get(`${base}/analytics/reports`, { headers })
  ).json();
  expect(reports.total).toBeGreaterThan(0);
  const storedReport = await (
    await request.get(`${base}/analytics/reports/${reports.items[0].id}`, {
      headers,
    })
  ).json();
  expect(storedReport.summary.samples).toBeGreaterThanOrEqual(12);
  expect(storedReport.summary.entries_estimate).toBeGreaterThanOrEqual(3);
  expect(storedReport.evidence_level).toBe("L0_SYNTHETIC");
  await panel
    .getByLabel("Relatórios no SQLite")
    .selectOption(reports.items[0].id);
  await expect(
    panel.getByRole("status", { name: "Resultado das análises" }),
  ).toContainText("Snapshot salvo");
  await panel.getByRole("button", { name: "Consultar histórico" }).click();
  await expect(panel.getByLabel("Posição no replay")).toBeVisible();
  await panel.screenshot({ path: "../../artifacts/analytics-desktop.png" });
  await page.setViewportSize({ width: 320, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await panel.screenshot({ path: "../../artifacts/analytics-mobile.png" });
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await panel.getByLabel("Provedor / fonte").selectOption("ruview-01");
  await panel.getByRole("button", { name: "Consultar histórico" }).click();
  await expect(
    panel.getByText("Nenhuma observação no intervalo selecionado."),
  ).toBeVisible();
  await page.setViewportSize({ width: 320, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  const input = panel.getByLabel("De", { exact: true });
  await input.focus();
  await expect(input).toBeFocused();
  await page.keyboard.press("Tab");
  expect(await page.evaluate(() => document.activeElement?.tagName)).toBe(
    "INPUT",
  );
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  expect(errors).toEqual([]);
});
