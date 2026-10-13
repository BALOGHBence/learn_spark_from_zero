import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The question bank lives in fixtures/questions at the repository root, outside
// this app's folder, so the dev server must be allowed to read from there.
const repoRoot = fileURLToPath(new URL("../..", import.meta.url));

export default defineConfig({
  plugins: [react()],
  base: "./",
  // The bundled question bank is about 1 MB.
  build: { chunkSizeWarningLimit: 2000 },
  server: { fs: { allow: [repoRoot] } },
});
