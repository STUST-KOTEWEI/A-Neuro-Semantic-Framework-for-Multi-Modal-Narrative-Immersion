/// <reference types="vitest" />
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

const repoName = "A-Neuro-Semantic-Framework-for-Multi-Modal-Narrative-Immersion"

// https://vitejs.dev/config/
export default defineConfig({
  base: `/${repoName}/`,
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.js",
  },
})
