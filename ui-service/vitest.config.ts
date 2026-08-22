import solidPlugin from "vite-plugin-solid";
import { defineConfig } from "vitest/config";

const FULL_COVERAGE = 100;
const TEST_TIMEOUT_MS = 30_000;

export default defineConfig({
  plugins: [solidPlugin({ hot: false })],
  server: {
    fs: {
      strict: false,
    },
  },
  resolve: {
    conditions: ["development", "browser"],
  },
  test: {
    environment: "jsdom",
    globals: true,
    testTimeout: TEST_TIMEOUT_MS,
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
    restoreMocks: true,
    coverage: {
      provider: "v8",
      include: ["src/**/*.ts", "src/**/*.tsx"],
      reporter: ["text-summary"],
      thresholds: {
        branches: FULL_COVERAGE,
        functions: FULL_COVERAGE,
        lines: FULL_COVERAGE,
        statements: FULL_COVERAGE,
      },
    },
  },
});
