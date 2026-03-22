import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/planner": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/retention": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
