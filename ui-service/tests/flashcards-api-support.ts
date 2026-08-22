import { afterEach, beforeEach, vi } from "vitest";
import fc from "fast-check";
import { Session } from "../src/shared/api/session";

export const SCOPE = fc.constantFrom("flashcard_deck", "folder" as const);
export const RATING = fc.constantFrom(1, 2, 3, 4 as const);

export function storedCard(
  overrides: Record<string, unknown> = {},
): Record<string, unknown> {
  return {
    id: 1,
    type: "basic",
    content: { front: "q", back: "a" },
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
