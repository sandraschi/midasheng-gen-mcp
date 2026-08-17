import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const BACKEND = "http://127.0.0.1:11159";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 11160,
    host: true,
    proxy: {
      "/api": { target: BACKEND, changeOrigin: true },
      "/mcp": { target: BACKEND, changeOrigin: true },
      "/docs": { target: BACKEND, changeOrigin: true },
      "/openapi.json": { target: BACKEND, changeOrigin: true },
      "/redoc": { target: BACKEND, changeOrigin: true },
    },
  },
  build: {
    outDir: "dist",
  },
});
