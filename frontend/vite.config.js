import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      // Optional: bypass CORS in local dev by proxying /api → backend
      // Usage: leave VITE_API_URL empty in .env and requests will hit the proxy
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});