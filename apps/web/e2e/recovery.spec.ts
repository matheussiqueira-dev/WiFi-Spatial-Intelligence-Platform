import { expect, test } from "@playwright/test";

// Native isolated Playwright stack only; never operate on an external operator database.
test.skip(
  process.env.E2E_EXTERNAL === "1",
  "Recovery injection uses the native isolated stack",
);
const token = "e2e-only-" + "x".repeat(40);

test("operator can pause and stop with an invalid draft configuration", async ({
  page,
  request,
}) => {
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  await expect(page.locator(".connection")).toContainText("Ao vivo");
  await page.getByLabel("Ocupantes", { exact: true }).fill("25");
  // Another local operator starts a valid session while this page has an invalid draft.
  const response = await request.post(
    "http://127.0.0.1:4810/api/v1/simulation/start",
    {
      headers: { Authorization: `Bearer ${token}` },
      data: { scenario: "walking", seed: 42, occupants: 2, speed: 1 },
    },
  );
  expect(response.ok()).toBe(true);
  await expect(page.locator(".state")).toHaveText("Em execução");
  await page.getByRole("button", { name: "Pausar", exact: true }).click();
  await expect(page.locator(".state")).toHaveText("Pausada");
  await page.getByRole("button", { name: "Parar", exact: true }).click();
  await expect(page.locator(".state")).toHaveText("Parada");
});

test("invalid stream closes without a browser exception or reconnect loop", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.addInitScript(() => {
    const Native = window.WebSocket;
    window.WebSocket = class extends Native {
      constructor(url: string | URL, protocols?: string | string[]) {
        super(url, protocols);
        let injected = false;
        this.addEventListener("message", () => {
          if (injected) return;
          injected = true;
          queueMicrotask(() =>
            this.dispatchEvent(new MessageEvent("message", { data: "{}" })),
          );
        });
      }
    };
  });
  await page.goto("/dashboard");
  await page.getByLabel("Token de acesso local").fill(token);
  await page.getByRole("button", { name: "Conectar", exact: true }).click();
  await expect(page.locator(".connection")).toContainText(
    "Dados incompatíveis",
  );
  await expect(page.locator(".error[role=alert]")).toContainText(
    "contrato sintético",
  );
  expect(errors).toEqual([]);
});
