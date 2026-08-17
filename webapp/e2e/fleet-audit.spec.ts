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
    // Settle: wait for the backend dot to reach Connected (health poll done)
    await expect(page.locator('[data-testid="backend-dot"]')).toContainText(
      /Connected|Offline/,
      { timeout: 15000 },
    );
    await page.waitForTimeout(2000);
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
    const routes: Record<string, string> = {
      "generate": "generate-page",
      "scenes": "scenes-page",
      "inbox": "inbox-page",
      "tools": "tools-page",
      "skills": "skills-page",
      "chat": "chat-page",
      "settings": "settings-page",
      "help": "help-page",
      "logs": "logs-page",
      "api-docs": "api-docs-page",
    };
    for (const [route, testid] of Object.entries(routes)) {
      await page.click(`[data-testid="nav-${route}"]`);
      await expect(page.locator(`[data-testid="${testid}"]`)).toBeVisible();
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
