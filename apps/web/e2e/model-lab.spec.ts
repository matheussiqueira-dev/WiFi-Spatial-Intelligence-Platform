import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("model lab: train, persist, export and reopen synthetic evaluation", async ({
  page,
}) => {
  if (
    process.env.E2E_EXTERNAL === "1" &&
    process.env.E2E_COMPOSE_PROJECT !== "wifi-spatial-native-e2e"
  )
    throw new Error("Requires isolated native stack");
  const token = process.env.E2E_TOKEN ?? "e2e-only-" + "x".repeat(40);
  async function connect() {
    await page.goto("/dashboard");
    await page.getByLabel("Token de acesso local").fill(token);
    await page.getByRole("button", { name: "Conectar", exact: true }).click();
  }
  await connect();
  await page
    .getByRole("button", { name: "Treinar e avaliar baseline" })
    .click();
  const result = page.getByLabel("Resultado do experimento", { exact: true });
  await expect(result).toContainText("L0_SYNTHETIC");
  await expect(result).toContainText("32 janelas de teste");
  const before = await result.innerText();
  const downloaded = page.waitForEvent("download");
  await page.getByRole("button", { name: "Exportar experimento JSON" }).click();
  expect((await downloaded).suggestedFilename()).toBe(
    "synthetic-experiment.json",
  );
  await connect();
  await page.getByRole("button", { name: "Consultar experimentos" }).click();
  await page
    .getByRole("button", { name: /^Abrir experimento/ })
    .first()
    .click();
  await expect(result).toHaveText(before, { useInnerText: true });
  await page.getByRole("button", { name: "Enfileirar baseline", exact: true }).click();
  await expect(page.getByLabel("Estado do job")).toContainText("completed");
  await expect(result).toContainText("L0_SYNTHETIC");
  await page.setViewportSize({ width: 320, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await page.screenshot({
    path: "../../artifacts/model-lab-mobile.png",
    fullPage: true,
  });
});
