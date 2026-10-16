import { expect, test } from "@playwright/test";

test("CSP: changing nonce and blocked unauthorized script", async ({
  page,
  request,
}) => {
  const first = await request.get("/dashboard");
  const second = await request.get("/dashboard");
  const policy = first.headers()["content-security-policy"];
  const nonce = policy.match(/'nonce-([^']+)'/)?.[1];
  expect(nonce).toBeTruthy();
  expect(second.headers()["content-security-policy"]).not.toContain(
    `'nonce-${nonce}'`,
  );
  expect(policy.split("script-src")[1].split(";")[0]).not.toContain(
    "unsafe-inline",
  );
  await page.addInitScript(() => {
    document.addEventListener("securitypolicyviolation", (event) => {
      if (event.violatedDirective.startsWith("script-src"))
        document.documentElement.dataset.cspBlocked = "yes";
    });
  });
  await page.route("**/dashboard", async (route) => {
    const response = await route.fetch();
    const body = (await response.text()).replace(
      "</body>",
      "<script>document.documentElement.dataset.unauthorized='yes'</script></body>",
    );
    await route.fulfill({ response, body });
  });
  await page.goto("/dashboard");
  await expect(
    page.getByRole("heading", { name: "Spatial Observatory" }),
  ).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("data-csp-blocked", "yes");
  expect(
    await page.locator("html").getAttribute("data-unauthorized"),
  ).toBeNull();
});
