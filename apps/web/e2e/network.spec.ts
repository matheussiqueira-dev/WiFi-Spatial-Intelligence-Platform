import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { e2eTarget } from "./target";

// Protocol fixtures are explicitly labelled; real host acquisition is verified separately.
test("network: authenticated telemetry ingestion, location comparison, export and mobile", async ({
  page,
  request,
}) => {
  const { token, apiBase: base } = e2eTarget();
  const headers = { Authorization: `Bearer ${token}` };
  const identifier = crypto.randomUUID();
  const payload = {
    sample_id: identifier,
    collector_id: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
    location: "Fixture Sala",
    link_state: "CONNECTED",
    signal_percent: 82,
    channel: 149,
    radio_type: "802.11ac",
    rx_mbps: 433.3,
    tx_mbps: 433.3,
    probe_sent: 3,
    probe_rtt_ms: [2, 3],
    probe_status: "COMPLETED",
  };
  const submitted = await request.post(`${base}/network/samples`, {
    headers,
    data: payload,
  });
  expect(submitted.ok()).toBe(true);
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  const panel = page.locator("#network");
  await expect(panel.getByTestId("network-signal")).toHaveText("82%");
  await expect(panel.getByTestId("network-link")).toHaveText("Conectado");
  await panel.getByLabel("Nome do ponto atual").fill("Fixture Quarto");
  await panel.getByRole("button", { name: "Definir ponto de medição" }).click();
  await expect(
    panel.getByRole("status").filter({ hasText: "próxima coleta" }),
  ).toBeVisible();
  expect((await request.get(`${base}/network/config`, { headers })).ok()).toBe(
    true,
  );
  await request.post(`${base}/network/samples`, {
    headers,
    data: {
      ...payload,
      sample_id: crypto.randomUUID(),
      location: "Fixture Quarto",
      signal_percent: 60,
      timestamp: new Date().toISOString(),
    },
  });
  await panel.getByRole("button", { name: "Atualizar diagnóstico" }).click();
  await expect(
    panel
      .getByLabel("Filtrar ponto")
      .getByRole("option", { name: "Fixture Quarto" }),
  ).toHaveCount(1);
  // Both fixtures lose 1 of 3 probes ("Fraco"); ties rank by signal, best first.
  const ranking = panel.getByRole("region", {
    name: "Comparação dos pontos Wi-Fi",
  });
  await expect(ranking.getByRole("row").nth(1)).toContainText("Fixture Sala");
  await expect(ranking.getByTestId("location-grade").first()).toHaveText(
    "Fraco",
  );
  // Two fresh samples: no baseline yet, so the panel abstains instead of alerting.
  await expect(panel.getByTestId("network-alerts")).toContainText(
    "Nenhum alerta",
  );
  await expect(panel.getByText("Sem comparação para:")).toBeVisible();
  // No receiver configured in the E2E stack: the panel explains instead of offering a test.
  await expect(panel.getByTestId("webhook-state")).toContainText(
    "Não configurado",
  );
  await expect(panel.getByRole("button", { name: "Enviar teste" })).toHaveCount(
    0,
  );
  const survey = await request.post(`${base}/network/channel-surveys`, {
    headers,
    data: {
      survey_id: crypto.randomUUID(),
      collector_id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      location: "Fixture Sala",
      channels: [
        {
          band: "5GHz",
          channel: 149,
          ap_count: 4,
          strongest_signal_percent: 90,
          utilization_percent: 60,
        },
      ],
    },
  });
  expect(survey.ok()).toBe(true);
  await panel.getByLabel("Filtrar ponto").selectOption("Fixture Sala");
  await expect(panel.getByTestId("network-signal")).toHaveText("82%");
  await expect(panel.getByTestId("channel-advice-5GHz")).toContainText(
    "Considerar o canal 36",
  );
  const capabilities = page.locator("#capabilities");
  await expect(capabilities.getByTestId("capability-profile")).toHaveText(
    "Perfil: lab",
  );
  await expect(
    capabilities.getByRole("row", { name: /Reidentificação/ }),
  ).toContainText("Desligada");
  const download = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Exportar medições CSV" }).click();
  expect((await download).suggestedFilename()).toBe("network-diagnostics.csv");
  const csv = await request.get(
    `${base}/network/export.csv?location=Fixture%20Sala`,
    { headers },
  );
  expect(await csv.text()).toContain("L2_LIVE_UNVALIDATED");
  expect(await csv.text()).not.toContain("SSID");
  // Erasure is scoped to the selected point and confirmed through a dialog.
  page.once("dialog", (dialog) => void dialog.accept());
  await panel
    .getByRole("button", { name: "Apagar medições deste ponto" })
    .click();
  await expect(
    panel.getByRole("status").filter({ hasText: "apagadas" }),
  ).toContainText("1 medições e 1 varreduras apagadas.");
  await expect(
    panel
      .getByLabel("Filtrar ponto")
      .getByRole("option", { name: "Fixture Sala" }),
  ).toHaveCount(0);
  await expect(
    panel
      .getByLabel("Filtrar ponto")
      .getByRole("option", { name: "Fixture Quarto" }),
  ).toHaveCount(1);
  await page.setViewportSize({ width: 320, height: 800 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect(
    (
      await new AxeBuilder({ page })
        .include("#network")
        .include("#capabilities")
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await panel.screenshot({ path: "../../artifacts/network-mobile.png" });
});
