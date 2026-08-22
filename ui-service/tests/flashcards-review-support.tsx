import { afterEach, vi } from "vitest";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import { FlashcardsReview } from "../src/features/flashcards/FlashcardsReview";
import { cardDue } from "./flashcard-factories";
import { renderAt } from "./router-support";

export const CARD = cardDue("1", null);
export const SECOND_CARD = {
  ...cardDue("2", null),
  face: { kind: "basic", front: "second", back: "answer" } as const,
};
export const INTERVALS = { 1: 60, 2: 600, 3: 86400, 4: 604800 };
export const TOMORROW = new Date(Date.now() + 86_400_000).toISOString();

export function deckOf(...cards: readonly (typeof CARD)[]): {
  totalFlashcards: number;
  flashcards: readonly (typeof CARD)[];
} {
  return { totalFlashcards: cards.length, flashcards: cards };
}

export function renderReview(): ReturnType<typeof renderAt> {
  return renderAt("/flashcard_deck/1", "/flashcard_deck/:id", () => (
    <AskProvider>
      <FlashcardsReview scope="flashcard_deck" scopeId="1" />
    </AskProvider>
  ));
}

afterEach(() => {
  vi.restoreAllMocks();
});
