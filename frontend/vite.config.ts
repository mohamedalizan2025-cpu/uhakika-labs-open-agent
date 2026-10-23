import { fileURLToPath, URL } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    // Dev-time proxy so the UI can call the FastAPI backend without CORS setup.
    // The backend URL is a local development default, not a credential.
    proxy: {
      "/health": "http://localhost:8000",
      "/run": "http://localhost:8000",
    },
  },
});
