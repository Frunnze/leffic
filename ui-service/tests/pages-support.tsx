import { afterEach, vi } from "vitest";
import { AccountApi } from "../src/features/settings/account-api";

export const NOTHING_DUE = {
  flashcardsDue: 0,
  testItemsDue: 0,
  notesDue: 0,
  doneToday: 0,
  totalToday: 0,
};

export const NOTE = {
  name: "Mitosis",
  content: "<p>cells divide</p>",
  readingMinutes: 2,
  isRead: false,
};

export function stubAccount(): void {
  vi.spyOn(AccountApi, "read").mockResolvedValue({
    username: "learner",
    email: "learner@example.test",
    theme: "system",
  });
}

afterEach(() => {
  vi.restoreAllMocks();
});
