import { test, expect } from "@playwright/test";

const BE = "http://127.0.0.1:11159";
const FE = "http://127.0.0.1:11160";

test.describe("Fleet Audit - midasheng-gen-mcp", () => {
  test("Backend health", async ({ request }) => {
    const resp = await request.get(`${BE}/api/health`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe("ok");
    expect(body.tool_count).toBeGreaterThanOrEqual(4);
  });

  test("Backend capabilities", async ({ request }) => {
    const resp = await request.get(`${BE}/api/capabilities`);
    expect(resp.status()).toBe(200);
  });

  test("Frontend loads without console errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    await page.goto(FE, { timeout: 20000 });
    await page.waitForTimeout(2500);
    await expect(page.locator("#root")).toBeAttached();
    expect(errors).toEqual([]);
  });

  test("Dashboard renders KPIs", async ({ page }) => {
    await page.goto(FE, { timeout: 20000 });
    await expect(page.locator('[data-testid="dashboard"]')).toBeAttached();
    await expect(page.locator('[data-testid="kpi-grid"]')).toBeAttached();
    await expect(page.locator('[data-testid="backend-dot"]')).toBeAttached();
  });

  test("Sidebar navigation walks all routes", async ({ page }) => {
    await page.goto(FE, { timeout: 20000 });
    const routes = [
      "generate",
      "scenes",
      "inbox",
      "tools",
      "skills",
      "chat",
      "settings",
      "help",
      "logs",
      "api-docs",
    ];
    for (const route of routes) {
      await page.click(`[data-testid="nav-${route}"]`);
      await page.waitForTimeout(800);
      const title = await page.locator('[data-testid="page-title"]').textContent();
      expect(title?.toLowerCase()).toContain(route.replace("-", " "));
    }
  });

  test("REST: scene pagination shape", async ({ request }) => {
    const resp = await request.get(`${BE}/api/scenes?limit=5&offset=0`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("items");
    expect(body).toHaveProperty("has_more");
    expect(body).toHaveProperty("total");
  });
});
