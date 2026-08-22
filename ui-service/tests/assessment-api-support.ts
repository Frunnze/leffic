import { afterEach, beforeEach, vi } from "vitest";
import fc from "fast-check";
import { Session } from "../src/shared/api/session";

export const SCOPE = fc.constantFrom("test", "folder" as const);

export function storedItem(
  overrides: Record<string, unknown> = {},
): Record<string, unknown> {
  return {
    id: 1,
    type: "multiple_choice",
    content: {
      question: "Why?",
      shuffled_options: [{ id: 0, option: "Because" }],
    },
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
