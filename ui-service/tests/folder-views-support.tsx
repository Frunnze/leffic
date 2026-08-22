import { afterEach, vi } from "vitest";
import fc from "fast-check";

export const COUNT = fc.integer({ min: 0, max: 20 });

export function breakdownOf(
  flashcardsDue: number,
  testItemsDue: number,
  notesDue: number,
): {
  flashcardsDue: number;
  testItemsDue: number;
  notesDue: number;
  doneToday: number;
  totalToday: number;
} {
  const due = flashcardsDue + testItemsDue + notesDue;

  return {
    flashcardsDue,
    testItemsDue,
    notesDue,
    doneToday: 2,
    totalToday: due + 2,
  };
}

afterEach(() => {
  vi.restoreAllMocks();
});
