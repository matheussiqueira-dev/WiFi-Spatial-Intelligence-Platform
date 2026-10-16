import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { e2eTarget } from "./target";

test("avatars: human and pet structures preserve occupancy, pause and mobile access", async ({
  page,
  request,
}) => {
  const { token, apiBase: base } = e2eTarget();
  const headers = { Authorization: `Bearer ${token}` };
  await request.post(`${base}/simulation/stop`, { headers });
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  const scene = page.locator("#observatory");
  await page.getByLabel("Ocupantes", { exact: true }).fill("3");
  await page.getByRole("button", { name: "Iniciar simulação" }).click();
  await expect(scene.getByTestId("occupant")).toHaveCount(3);
  await expect(scene.locator('[data-avatar="human"]')).toHaveCount(3);
  await expect(scene.locator("[data-joint]")).toHaveCount(51);
  await scene.getByLabel("Avatares da cena").selectOption("mixed");
  for (const kind of ["human", "dog", "cat"])
    await expect(scene.locator(`[data-avatar="${kind}"]`)).toHaveCount(1);
  await expect(page.getByTestId("occupancy")).toContainText("3");
  await scene.getByLabel("Volume dos corpos").uncheck();
  await expect(scene.getByTestId("avatar-volume")).toHaveCount(0);
  await scene.getByLabel("Volume dos corpos").check();
  await page.getByRole("button", { name: "Pausar", exact: true }).click();
  await expect(page.locator(".state")).toHaveText("Pausada");
  await scene.getByRole("button", { name: "Ampliar / reduzir cena" }).click();
  await expect
    .poll(() => page.evaluate(() => document.fullscreenElement !== null))
    .toBe(true);
  expect(
    await scene
      .locator(".scene-viewer")
      .evaluate((element) => element.scrollWidth <= element.clientWidth),
  ).toBe(true);
  await page.screenshot({ path: "../../artifacts/articulated-immersive.png" });
  await scene.getByRole("button", { name: "Ampliar / reduzir cena" }).click();
  await expect
    .poll(() => page.evaluate(() => document.fullscreenElement === null))
    .toBe(true);
  await page.screenshot({
    path: "../../artifacts/articulated-desktop.png",
    fullPage: true,
  });
  await scene.getByLabel("Visualização").selectOption("plan");
  await expect(scene.getByTestId("occupant")).toHaveCount(3);
  await expect(scene.locator("[data-joint]")).toHaveCount(0);
  await scene.getByLabel("Visualização").selectOption("structure");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(scene.getByLabel("Articular avatares")).toBeDisabled();
  await expect(scene.getByLabel("Articular avatares")).not.toBeChecked();
  await page.setViewportSize({ width: 320, height: 800 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "../../artifacts/articulated-mobile.png",
    fullPage: true,
  });
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await page.getByRole("button", { name: "Parar", exact: true }).click();
});
