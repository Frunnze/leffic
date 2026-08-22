import { onCleanup, onMount } from "solid-js";
import type { FlashcardRating } from "./flashcard-models";

const RATING_KEYS: Readonly<Record<string, FlashcardRating>> = {
  "1": 1,
  "2": 2,
  "3": 3,
  "4": 4,
};

type FlashcardShortcutHandlers = {
  readonly isAnswerShown: () => boolean;
  readonly onReveal: () => void;
  readonly onRate: (rating: FlashcardRating) => void;
};

export class FlashcardShortcuts {
  static bind(handlers: FlashcardShortcutHandlers): void {
    const handleKeyDown = (event: KeyboardEvent): void => {
      if (FlashcardShortcuts.isTypingTarget(event.target)) return;

      if (event.key === " ") {
        event.preventDefault();
        if (!handlers.isAnswerShown()) handlers.onReveal();
        return;
      }

      const rating = RATING_KEYS[event.key];
      if (rating === undefined || !handlers.isAnswerShown()) return;

      event.preventDefault();
      handlers.onRate(rating);
    };

    onMount(() => { document.addEventListener("keydown", handleKeyDown); });
    onCleanup(() => { document.removeEventListener("keydown", handleKeyDown); });
  }

  private static isTypingTarget(target: EventTarget | null): boolean {
    return (
      target instanceof HTMLInputElement ||
      target instanceof HTMLTextAreaElement
    );
  }
}
