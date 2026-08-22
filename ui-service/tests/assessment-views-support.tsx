import { afterEach, beforeEach, vi } from "vitest";
import type {
  AssessmentItem,
} from "../src/features/assessment/assessment-models";

export const MULTIPLE_CHOICE: AssessmentItem = {
  id: "1",
  type: "multiple_choice",
  question: "Why does the sky look blue?",
  options: [
    { id: 0, option: "Rayleigh scattering" },
    { id: 1, option: "Reflected ocean" },
  ],
  lastAnswers: [],
};

export const SHORT_ANSWER: AssessmentItem = {
  id: "2",
  type: "short_answer",
  question: "Name the process",
  options: [],
  lastAnswers: [],
};

export function pageOf(
  items: readonly AssessmentItem[],
  page = 1,
  totalItems = items.length,
): {
  testSession: string;
  items: readonly AssessmentItem[];
  page: number;
  perPage: number;
  totalItems: number;
} {
  return { testSession: "session", items, page, perPage: 2, totalItems };
}

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.restoreAllMocks();
});
