import { describe, expect, it, vi } from "vitest";
import { render } from "@solidjs/testing-library";
import fc from "fast-check";
import {
  FlashcardShortcuts,
} from "../src/features/flashcards/flashcard-shortcuts";
import type {
  FlashcardRating,
} from "../src/features/flashcards/flashcard-models";

type Bound = {
  readonly onReveal: ReturnType<typeof vi.fn>;
  readonly onRate: ReturnType<typeof vi.fn>;
  readonly unmount: () => void;
};

function bind(isAnswerShown: boolean): Bound {
  const onReveal = vi.fn();
  const onRate = vi.fn();
  const { unmount } = render(() => {
    FlashcardShortcuts.bind({
      isAnswerShown: () => isAnswerShown,
      onReveal,
      onRate,
    });

    return <input type="text" />;
  });

  return { onReveal, onRate, unmount };
}

function press(key: string, target: EventTarget = document): void {
  const event = new KeyboardEvent("keydown", {
    key,
    bubbles: true,
    cancelable: true,
  });
  target.dispatchEvent(event);
}

describe("FlashcardShortcuts.bind", () => {
  it("bind property rates the card on its number key once the answer shows", () => {
    fc.assert(
      fc.property(fc.constantFrom<FlashcardRating>(1, 2, 3, 4), (rating) => {
        const bound = bind(true);

        press(String(rating));

        expect(bound.onRate).toHaveBeenCalledWith(rating);
        bound.unmount();
      }),
    );
  });

  it("bind property refuses to rate while the answer is still hidden", () => {
    fc.assert(
      fc.property(fc.constantFrom<FlashcardRating>(1, 2, 3, 4), (rating) => {
        const bound = bind(false);

        press(String(rating));

        expect(bound.onRate).not.toHaveBeenCalled();
        bound.unmount();
      }),
    );
  });

  it("reveals the answer on the space bar", () => {
    const bound = bind(false);

    press(" ");

    expect(bound.onReveal).toHaveBeenCalledTimes(1);
    bound.unmount();
  });

  it("does not reveal an answer that already shows", () => {
    const bound = bind(true);

    press(" ");

    expect(bound.onReveal).not.toHaveBeenCalled();
    bound.unmount();
  });

  it("ignores a key pressed while typing in a field", () => {
    const bound = bind(true);

    press("1", document.querySelector("input") ?? document);

    expect(bound.onRate).not.toHaveBeenCalled();
    bound.unmount();
  });

  it("ignores a key that means nothing to the reviewer", () => {
    const bound = bind(true);

    press("q");

    expect(bound.onRate).not.toHaveBeenCalled();
    expect(bound.onReveal).not.toHaveBeenCalled();
    bound.unmount();
  });

  it("stops listening once the reviewer is gone", () => {
    const bound = bind(true);
    bound.unmount();

    press("1");

    expect(bound.onRate).not.toHaveBeenCalled();
  });
});

describe("FlashcardShortcuts.isTypingTarget", () => {
  it("isTypingTarget property ignores every key pressed inside a field", () => {
    fc.assert(
      fc.property(fc.constantFrom("input", "textarea"), (tagName) => {
        const bound = bind(true);
        const field = document.createElement(tagName);
        document.body.append(field);

        press("1", field);

        expect(bound.onRate).not.toHaveBeenCalled();
        field.remove();
        bound.unmount();
      }),
    );
  });

  it("isTypingTarget property lets a key through from anywhere else", () => {
    fc.assert(
      fc.property(fc.constantFrom("div", "span", "button"), (tagName) => {
        const bound = bind(true);
        const elsewhere = document.createElement(tagName);
        document.body.append(elsewhere);

        press("1", elsewhere);

        expect(bound.onRate).toHaveBeenCalledWith(1);
        elsewhere.remove();
        bound.unmount();
      }),
    );
  });
});
