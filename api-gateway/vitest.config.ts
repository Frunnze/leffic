import { defineConfig } from "vitest/config";

const FULL_COVERAGE = 100;
const TEST_TIMEOUT_MS = 30_000;

export default defineConfig({
  test: {
    environment: "node",
    testTimeout: TEST_TIMEOUT_MS,
    include: ["tests/**/*.test.ts"],
    restoreMocks: true,
    coverage: {
      provider: "v8",
      include: ["src/**/*.ts"],
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
