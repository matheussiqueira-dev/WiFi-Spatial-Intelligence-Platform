import { expect, test } from "@playwright/test";
import { e2eTarget } from "./target";

test("automation: persisted dry-run decision and revocation", async ({
  page,
  request,
}) => {
  const { token, apiBase: base } = e2eTarget();
  const headers = { Authorization: `Bearer ${token}` };
  const decisionTotal = async () => {
    const response = await request.get(`${base}/automation/decisions`, {
      headers,
    });
    expect(response.ok()).toBe(true);
    return (await response.json()).total as number;
  };
  expect(
    (await request.post(`${base}/simulation/stop`, { headers })).ok(),
  ).toBe(true);
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  const created = page.waitForResponse(
    (response) =>
      response.url().endsWith("/automation/rules") &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Criar regra dry-run" }).click();
  const createdResponse = await created;
  expect(createdResponse.ok()).toBe(true);
  const rule = await createdResponse.json();
  const revoke = page
    .locator(`[data-rule-id="${rule.id}"]`)
    .getByRole("button");
  await expect(revoke).toBeEnabled();
  // Compare with the count before this run; reused databases may hold decisions.
  const before = await decisionTotal();
  const first = await request.post(`${base}/simulation/start`, {
    headers,
    data: { occupants: 2, speed: 4 },
  });
  expect(first.ok()).toBe(true);
  await expect.poll(decisionTotal).toBeGreaterThan(before);
  expect(
    (await request.post(`${base}/simulation/stop`, { headers })).ok(),
  ).toBe(true);
  await page
    .getByRole("button", { name: "Atualizar regras e decisões" })
    .click();
  await expect(page.getByLabel("Decisões dry-run")).toContainText(
    "sem despacho",
  );
  await revoke.click();
  await expect(revoke).toBeDisabled();
  const count = await decisionTotal();
  const restarted = await request.post(`${base}/simulation/start`, {
    headers,
    data: { occupants: 2, speed: 4 },
  });
  expect(restarted.ok()).toBe(true);
  expect((await restarted.json()).produced_events).toBe(0);
  await expect
    .poll(
      async () =>
        (await (await request.get(`${base}/system/status`, { headers })).json())
          .produced_events,
    )
    .toBeGreaterThan(1);
  expect(
    (await request.post(`${base}/simulation/stop`, { headers })).ok(),
  ).toBe(true);
  expect(await decisionTotal()).toBe(count);
});
