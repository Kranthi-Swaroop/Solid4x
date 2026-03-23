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
        target: "https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app",
        changeOrigin: true,
      },
      "/static": {
        target: "https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app",
        changeOrigin: true,
      },
      "/syllabus": {
        target: "https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app",
        changeOrigin: true,
      },
      "/planner": {
        target: "https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app",
        changeOrigin: true,
      },
      "/retention": {
        target: "https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app",
        changeOrigin: true,
      },
      "/dashboard": {
        target: "https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app",
        changeOrigin: true,
      },
    },
  },
});
