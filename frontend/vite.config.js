import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api/chat": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
      "/api/tts": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/planner": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/retention": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/dashboard": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/syllabus": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },

      "/static": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
