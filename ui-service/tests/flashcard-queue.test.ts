import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { FlashcardQueue } from "../src/features/flashcards/flashcard-queue";
import { cardDue, dueDate, flashcard } from "./flashcard-factories";

const YESTERDAY = "2020-01-01T00:00:00.000Z";
const TOMORROW = "2999-01-01T00:00:00.000Z";

describe("FlashcardQueue.isToday", () => {
  it("isToday property holds for every hour of the current day", () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 23 }), (hour) => {
        const moment = new Date();
        moment.setUTCHours(hour, 0, 0, 0);

        expect(FlashcardQueue.isToday(moment)).toBe(true);
      }),
    );
  });

  it("isToday property fails for any moment years away", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 40 }), (years) => {
        const moment = new Date();
        moment.setUTCFullYear(moment.getUTCFullYear() + years);

        expect(FlashcardQueue.isToday(moment)).toBe(false);
      }),
    );
  });

  it("rejects the same day in a different month", () => {
    const moment = new Date();
    moment.setUTCMonth((moment.getUTCMonth() + 1) % 12);
    moment.setUTCDate(moment.getUTCDate());

    expect(FlashcardQueue.isToday(moment)).toBe(
      moment.getUTCDate() === new Date().getUTCDate() &&
        moment.getUTCMonth() === new Date().getUTCMonth(),
    );
  });
});

describe("FlashcardQueue.sortByDueDate", () => {
  it("sortByDueDate property keeps every card it was given", () => {
    fc.assert(
      fc.property(fc.array(flashcard), (cards) => {
        expect(FlashcardQueue.sortByDueDate(cards)).toHaveLength(cards.length);
      }),
    );
  });

  it("sortByDueDate property puts every unscheduled card first", () => {
    fc.assert(
      fc.property(fc.array(flashcard, { minLength: 1 }), (cards) => {
        const sorted = FlashcardQueue.sortByDueDate(cards);
        const unscheduled = sorted.filter((card) => card.nextReview === null);

        expect(sorted.slice(0, unscheduled.length)).toEqual(unscheduled);
      }),
    );
  });

  it("sortByDueDate property orders scheduled cards oldest first", () => {
    fc.assert(
      fc.property(fc.array(dueDate, { minLength: 2 }), (dates) => {
        const cards = dates.map((date, index) => cardDue(String(index), date));
        const sorted = FlashcardQueue.sortByDueDate(cards);
        const times = sorted.map((card) =>
          new Date(card.nextReview ?? "").getTime(),
        );

        expect(times).toEqual([...times].sort((left, right) => left - right));
      }),
    );
  });

  it("leaves two unscheduled cards in the order they arrived", () => {
    const first = cardDue("first", null);
    const second = cardDue("second", null);

    expect(FlashcardQueue.sortByDueDate([first, second])).toEqual([
      first,
      second,
    ]);
  });
});

describe("FlashcardQueue.afterReview", () => {
  it("afterReview property never grows the queue", () => {
    fc.assert(
      fc.property(dueDate, (date) => {
        const cards = [cardDue("a", YESTERDAY), cardDue("b", TOMORROW)];
        const result = { dueDate: date, newFsrsCard: {} };

        expect(
          FlashcardQueue.afterReview(cards, result).length,
        ).toBeLessThanOrEqual(cards.length);
      }),
    );
  });

  it("hands back an empty queue untouched", () => {
    const result = { dueDate: TOMORROW, newFsrsCard: {} };

    expect(FlashcardQueue.afterReview([], result)).toEqual([]);
  });

  it("drops the card when its next review is past every other", () => {
    const cards = [cardDue("a", YESTERDAY), cardDue("b", YESTERDAY)];
    const result = { dueDate: TOMORROW, newFsrsCard: { step: 1 } };

    expect(FlashcardQueue.afterReview(cards, result)).toEqual([
      cardDue("b", YESTERDAY),
    ]);
  });

  it("keeps the card and re-sorts when it is due again soonest", () => {
    const cards = [cardDue("a", TOMORROW), cardDue("b", TOMORROW)];
    const result = { dueDate: YESTERDAY, newFsrsCard: { step: 2 } };
    const remaining = FlashcardQueue.afterReview(cards, result);

    expect(remaining.map((card) => card.id)).toEqual(["a", "b"]);
    expect(remaining[0]?.fsrsCard).toEqual({ step: 2 });
  });

  it("drops the card when nothing behind it is scheduled", () => {
    const cards = [cardDue("a", YESTERDAY), cardDue("b", null)];
    const result = { dueDate: TOMORROW, newFsrsCard: {} };

    expect(FlashcardQueue.afterReview(cards, result)).toEqual([
      cardDue("b", null),
    ]);
  });
});

describe("FlashcardQueue.leavesQueue", () => {
  it("leavesQueue property drops a card scheduled past everything left", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 30 }), (days) => {
        const later = new Date(Date.parse(YESTERDAY) + days * 86_400_000);
        const cards = [cardDue("a", YESTERDAY), cardDue("b", YESTERDAY)];
        const result = { dueDate: later.toISOString(), newFsrsCard: {} };

        expect(FlashcardQueue.afterReview(cards, result)).toHaveLength(1);
      }),
    );
  });

  it("leavesQueue property keeps a card due before everything left", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 30 }), (days) => {
        const earlier = new Date(Date.parse(TOMORROW) - days * 86_400_000);
        const cards = [cardDue("a", TOMORROW), cardDue("b", TOMORROW)];
        const result = { dueDate: earlier.toISOString(), newFsrsCard: {} };

        expect(FlashcardQueue.afterReview(cards, result)).toHaveLength(2);
      }),
    );
  });
});
