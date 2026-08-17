import { defineConfig } from "@playwright/test";

const FE = "http://127.0.0.1:11160";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  retries: 1,
  use: {
    baseURL: FE,
    headless: true,
    screenshot: "only-on-failure",
  },
  projects: [{ name: "fleet-audit", testMatch: /fleet-audit\.spec\.ts/ }],
  webServer: {
    command: `uv run python -m midasheng_gen_mcp --mode http --host 127.0.0.1 --port 11159`,
    port: 11159,
    cwd: "../",
    timeout: 60000,
    reuseExistingServer: true,
    env: {
      MIDASHENG_BACKEND_PORT: "11159",
    },
  },
});
