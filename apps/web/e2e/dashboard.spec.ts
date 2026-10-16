import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import path from "node:path";
import AxeBuilder from "@axe-core/playwright";

const external = process.env.E2E_EXTERNAL === "1";
const token =
  process.env.E2E_TOKEN ??
  (external
    ? (readFileSync(path.resolve(__dirname, "../../../.env"), "utf8")
        .match(/^SPATIAL_TOKEN=(.+)$/m)?.[1]
        ?.trim() ?? "")
    : "e2e-only-" + "x".repeat(40));
const apiBase = `http://127.0.0.1:${external ? Number(process.env.E2E_API_PORT ?? 8000) : 4810}/api/v1`;
if (
  external &&
  !["wifi-spatial-verification", "wifi-spatial-native-e2e"].includes(
    process.env.E2E_COMPOSE_PROJECT ?? "",
  )
) {
  throw new Error(
    "External tests require the isolated wifi-spatial-verification stack.",
  );
}

test("local MVP: auth, live stream, controls, history, mobile and deletion", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  await page.addInitScript(() => {
    const Native = window.WebSocket;
    const sockets: WebSocket[] = [];
    window.WebSocket = class extends Native {
      constructor(url: string | URL, protocols?: string | string[]) {
        super(url, protocols);
        sockets.push(this);
      }
    };
    window.addEventListener("test-disconnect", () =>
      sockets.forEach((socket) => socket.close()),
    );
  });
  page.on("pageerror", (error) => errors.push(error.message));
  const auth = { Authorization: `Bearer ${token}` };
  await request.post(`${apiBase}/simulation/stop`, { headers: auth });
  await request.delete(`${apiBase}/events/synthetic`, { headers: auth });
  const response = await page.goto("/dashboard");
  expect(response?.headers()["x-content-type-options"]).toBe("nosniff");
  expect(response?.headers()["x-frame-options"]).toBe("DENY");
  expect(response?.headers()["content-security-policy"]).toContain(
    "object-src 'none'",
  );
  await expect(
    page.getByRole("heading", { name: "Spatial Observatory" }),
  ).toBeVisible();
  await page
    .getByLabel("Token de acesso local")
    .fill("wrong-" + "x".repeat(32));
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  await expect(page.locator(".error[role=alert]")).toContainText(
    "Token inválido",
  );
  const streamEvent = new Promise<void>((resolve) =>
    page.on("websocket", (ws) =>
      ws.on("framereceived", (frame) => {
        if (/"type":\s*"event"/.test(frame.payload.toString())) resolve();
      }),
    ),
  );
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  await expect(page.locator(".connection")).toContainText("Ao vivo");
  await expect(page.getByTestId("virtual-sensor")).toHaveCount(6);
  await page.getByLabel("Cenário", { exact: true }).selectOption("stationary");
  await page.getByLabel("Ocupantes", { exact: true }).fill("3");
  await page.getByLabel("Velocidade").selectOption("4");
  await page.getByRole("button", { name: "Iniciar simulação" }).click();
  await streamEvent;
  await expect(page.getByTestId("occupant")).toHaveCount(3);
  await expect(page.getByTestId("presence")).toHaveText("Detectada");
  await expect(page.locator("#history tbody tr").first()).toContainText(
    "L0_SYNTHETIC",
  );
  await expect
    .poll(
      async () =>
        (
          await (
            await request.get(`${apiBase}/events`, { headers: auth })
          ).json()
        ).total,
    )
    .toBeGreaterThanOrEqual(24);
  await page.getByRole("button", { name: "Pausar", exact: true }).click();
  await expect(page.locator(".state")).toHaveText("Pausada");
  const paused = (
    await (await request.get(`${apiBase}/events`, { headers: auth })).json()
  ).total;
  await page.waitForTimeout(450);
  expect(
    (await (await request.get(`${apiBase}/events`, { headers: auth })).json())
      .total,
  ).toBe(paused);
  await page.getByRole("button", { name: "Continuar", exact: true }).click();
  await expect(page.locator(".state")).toHaveText("Em execução");
  await expect
    .poll(
      async () =>
        (
          await (
            await request.get(`${apiBase}/events`, { headers: auth })
          ).json()
        ).total,
    )
    .toBeGreaterThan(paused);
  await page.getByRole("button", { name: "Parar", exact: true }).click();
  await expect(page.locator(".state")).toHaveText("Parada");
  await expect(
    page.getByRole("button", { name: "Próxima", exact: true }),
  ).toBeEnabled();
  const firstTick = await page
    .locator("#history tbody tr")
    .first()
    .locator("td")
    .last()
    .textContent();
  await page.getByRole("button", { name: "Próxima", exact: true }).click();
  await expect(
    page.locator("#history tbody tr").first().locator("td").last(),
  ).not.toHaveText(firstTick ?? "");
  await page.getByRole("button", { name: "Anterior", exact: true }).click();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: "../../artifacts/dashboard-desktop.png",
    fullPage: true,
  });
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  const persisted = (
    await (await request.get(`${apiBase}/events`, { headers: auth })).json()
  ).total;
  await page.reload();
  await expect(page.getByLabel("Token de acesso local")).toHaveValue("");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  await expect(page.locator("#history tbody tr")).toHaveCount(
    Math.min(20, persisted),
  );
  await expect(page.locator(".connection")).toContainText("Ao vivo");
  await page.evaluate(() => window.dispatchEvent(new Event("test-disconnect")));
  await expect(page.locator(".connection")).toContainText("Reconectando");
  await expect(page.locator(".connection")).toContainText("Ao vivo");
  expect(
    await page.evaluate(() => ({
      local: localStorage.length,
      session: sessionStorage.length,
    })),
  ).toEqual({ local: 0, session: 0 });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(
    page.getByRole("button", { name: "Iniciar simulação" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "../../artifacts/dashboard-mobile.png",
    fullPage: true,
  });
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Apagar eventos sintéticos" }).click();
  await expect(page.getByText("Nenhum evento nesta página")).toBeVisible();
  expect(
    (await (await request.get(`${apiBase}/events`, { headers: auth })).json())
      .total,
  ).toBe(0);
  expect(errors).toEqual([]);
});
