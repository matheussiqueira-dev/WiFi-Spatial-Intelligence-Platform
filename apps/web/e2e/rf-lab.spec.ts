import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { e2eTarget } from "./target";

test("rf lab: synthetic fingerprint evaluation and verified model registry", async ({
  page,
  request,
}) => {
  const { token, apiBase: base } = e2eTarget();
  const headers = { Authorization: `Bearer ${token}` };
  const run = await request.post(`${base}/model-lab/runs`, {
    headers,
    data: { seed: 11 },
  });
  expect(run.ok()).toBe(true);
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  const panel = page.locator("#rf-lab");
  await panel.getByRole("button", { name: "Avaliar impressão RF" }).click();
  const results = panel.getByTestId("rf-results");
  await expect(results).toContainText("Mudanças sutis detectadas");
  await expect(results).toContainText("Alarmes falsos (mesmo ambiente)");
  await expect(panel.getByText(/não identifica objeto/).first()).toBeVisible();
  await expect(panel.getByTestId("model-integrity").first()).toHaveText(
    "Íntegro",
  );
  expect(
    (
      await new AxeBuilder({ page })
        .include("#rf-lab")
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
});
