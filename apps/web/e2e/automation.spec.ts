import { expect, test } from "@playwright/test";

test("automation: persisted dry-run decision and revocation", async ({
  page,
  request,
}) => {
  const external = process.env.E2E_EXTERNAL === "1";
  if (external && process.env.E2E_COMPOSE_PROJECT !== "wifi-spatial-native-e2e")
    throw new Error("Isolated stack required");
  const token = process.env.E2E_TOKEN ?? "e2e-only-" + "x".repeat(40);
  const base = `http://127.0.0.1:${external ? Number(process.env.E2E_API_PORT ?? 8000) : 4810}/api/v1`;
  const headers = { Authorization: `Bearer ${token}` };
  await request.post(`${base}/simulation/stop`, { headers });
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  const created = page.waitForResponse(
    (response) =>
      response.url().endsWith("/automation/rules") &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Criar regra dry-run" }).click();
  const rule = await (await created).json();
  const revoke = page
    .locator(`[data-rule-id="${rule.id}"]`)
    .getByRole("button");
  await expect(revoke).toBeEnabled();
  await request.post(`${base}/simulation/start`, {
    headers,
    data: { occupants: 2, speed: 4 },
  });
  await expect
    .poll(
      async () =>
        (
          await (
            await request.get(`${base}/automation/decisions`, { headers })
          ).json()
        ).total,
    )
    .toBeGreaterThan(0);
  await request.post(`${base}/simulation/stop`, { headers });
  await page
    .getByRole("button", { name: "Atualizar regras e decisões" })
    .click();
  await expect(page.getByLabel("Decisões dry-run")).toContainText(
    "sem despacho",
  );
  await revoke.click();
  await expect(revoke).toBeDisabled();
  const count = (
    await (
      await request.get(`${base}/automation/decisions`, { headers })
    ).json()
  ).total;
  await request.post(`${base}/simulation/start`, {
    headers,
    data: { occupants: 2, speed: 4 },
  });
  await expect
    .poll(
      async () =>
        (await (await request.get(`${base}/system/status`, { headers })).json())
          .produced_events,
    )
    .toBeGreaterThan(1);
  await request.post(`${base}/simulation/stop`, { headers });
  expect(
    (
      await (
        await request.get(`${base}/automation/decisions`, { headers })
      ).json()
    ).total,
  ).toBe(count);
});
