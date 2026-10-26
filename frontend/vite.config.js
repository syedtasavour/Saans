import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies /api and /health to the FastAPI backend so the frontend
// can use same-origin relative URLs (no CORS juggling in the browser).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8077", changeOrigin: true },
      "/health": { target: "http://localhost:8077", changeOrigin: true },
    },
  },
});
