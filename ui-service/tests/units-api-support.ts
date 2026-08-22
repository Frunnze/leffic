import { afterEach, beforeEach, vi } from "vitest";
import { Session } from "../src/shared/api/session";

export function storedUnit(
  overrides: Record<string, unknown> = {},
): Record<string, unknown> {
  return {
    id: "1",
    name: "A note",
    type: "note",
    created_at: "2024-01-01T00:00:00.000Z",
    ...overrides,
  };
}

beforeEach(() => {
  Session.store("token");
});

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});
