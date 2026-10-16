import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { e2eTarget } from "./target";

// Runs only with E2E_PROFILE=commercial-br (see playwright.config.ts): the API is
// started with SPATIAL_CAPABILITY_PROFILE=commercial-br, so group B must be refused.
test("commercial-br: only network diagnostics, no spatial stream or data", async ({
  page,
  request,
}) => {
  const { token, apiBase: base } = e2eTarget();
  const headers = { Authorization: `Bearer ${token}` };
  const catalog = await request.get(`${base}/capabilities`, { headers });
  expect((await catalog.json()).profile).toBe("commercial-br");
  for (const path of [
    "/events",
    "/sensors",
    "/analytics/replay",
    "/automation/rules",
  ]) {
    const refused = await request.get(`${base}${path}`, { headers });
    expect(refused.status(), path).toBe(403);
  }
  expect((await request.get(`${base}/network/report`, { headers })).ok()).toBe(
    true,
  );

  const sockets: string[] = [];
  page.on("websocket", (socket) => sockets.push(socket.url()));
  const spatialCalls: string[] = [];
  page.on("request", (call) => {
    if (/\/api\/v1\/(events|sensors|occupancy|analytics)/.test(call.url()))
      spatialCalls.push(call.url());
  });
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  await expect(page.getByTestId("spatial-disabled")).toBeVisible();
  await expect(page.locator("#network")).toBeVisible();
  const nav = page.getByRole("navigation", { name: "Navegação principal" });
  await expect(
    nav.getByRole("link", { name: "Diagnóstico Wi-Fi" }),
  ).toBeVisible();
  for (const hidden of [
    "Observatório",
    "Simulação",
    "Histórico",
    "Análises e replay",
  ])
    await expect(nav.getByRole("link", { name: hidden })).toHaveCount(0);
  await expect(
    page.locator("#observatory, #simulation, #analytics"),
  ).toHaveCount(0);
  // Give a mistaken effect time to open the stream or poll before asserting absence.
  await page.waitForTimeout(1500);
  expect(sockets).toEqual([]);
  expect(spatialCalls).toEqual([]);
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
});
