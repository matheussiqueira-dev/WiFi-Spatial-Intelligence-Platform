import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { e2eTarget } from "./target";

const WCAG = ["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"];

async function login(page: Page, token: string) {
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
}

test("access roles: admin issues a viewer token; viewer sees no write controls", async ({
  page,
  request,
}) => {
  const { token, apiBase } = e2eTarget();
  const auth = { Authorization: `Bearer ${token}` };
  expect(
    (await request.post(`${apiBase}/simulation/stop`, { headers: auth })).ok(),
  ).toBe(true);

  // Bootstrap admin issues the token through the dashboard and reads it once.
  await login(page, token);
  await expect(page.getByTestId("role")).toHaveText(
    "Administração · token de bootstrap",
  );
  const panel = page.getByTestId("access-panel");
  await expect(panel).toBeVisible();
  const label = `Leitura E2E ${Date.now()}`;
  await panel.getByLabel("Nome da pessoa ou dispositivo").fill(label);
  await panel.getByLabel("Papel").selectOption("viewer");
  await panel.getByRole("button", { name: "Emitir token" }).click();
  const issued = panel.getByTestId("issued-token").getByRole("textbox");
  await expect(issued).toHaveValue(/^wsp_/);
  const viewerToken = await issued.inputValue();
  expect(
    (await new AxeBuilder({ page }).include("#access").withTags(WCAG).analyze())
      .violations,
  ).toEqual([]);
  await panel.getByRole("button", { name: "Já guardei, ocultar" }).click();
  await expect(panel.getByTestId("issued-token")).toHaveCount(0);
  // The listing never shows the value again.
  await expect(panel).not.toContainText(viewerToken);
  await page.getByRole("button", { name: "Sair" }).click();

  // Viewer: reads and watches the stream, every write control is absent.
  await login(page, viewerToken);
  await expect(page.getByTestId("role")).toHaveText(`Leitura · ${label}`);
  await expect(page.locator(".connection")).toContainText("Ao vivo");
  await expect(page.getByTestId("read-only")).toBeVisible();
  for (const name of [
    "Iniciar simulação",
    "Pausar",
    "Parar",
    "Apagar eventos sintéticos",
    "Definir ponto de medição",
    "Apagar histórico de rede",
    "Salvar relatório",
    "Treinar e avaliar baseline",
    "Enfileirar baseline",
    "Criar regra dry-run",
    "Emitir token",
  ])
    await expect(page.getByRole("button", { name, exact: true })).toHaveCount(
      0,
    );
  await expect(page.getByTestId("access-panel")).toHaveCount(0);
  await expect(page.locator("#source")).toHaveCount(0);
  // Read surfaces stay available.
  await expect(
    page.getByRole("heading", { name: "Histórico de eventos" }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => ({
      local: localStorage.length,
      session: sessionStorage.length,
      url: location.href,
    })),
  ).toEqual({ local: 0, session: 0, url: expect.not.stringContaining("wsp_") });
  expect(
    (await new AxeBuilder({ page }).withTags(WCAG).analyze()).violations,
  ).toEqual([]);

  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByTestId("role")).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);

  // The API refuses the viewer regardless of the interface.
  const refused = await request.post(`${apiBase}/simulation/start`, {
    headers: { Authorization: `Bearer ${viewerToken}` },
    data: { speed: 1 },
  });
  expect(refused.status()).toBe(403);

  // Revocation by the admin ends the viewer session on the next request.
  const listing = await (
    await request.get(`${apiBase}/access/tokens`, { headers: auth })
  ).json();
  const id = listing.items.find(
    (item: { label: string }) => item.label === label,
  ).id;
  expect(
    (
      await request.post(`${apiBase}/access/tokens/${id}/revoke`, {
        headers: auth,
      })
    ).ok(),
  ).toBe(true);
  await expect(
    page.getByRole("alert").filter({ hasText: "Token inválido" }),
  ).toBeVisible();
  await expect(page.locator(".connection")).toContainText("Acesso recusado");
});
