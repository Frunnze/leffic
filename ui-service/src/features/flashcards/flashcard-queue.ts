import type { Flashcard, FlashcardReviewResult } from "./flashcard-models";

export class FlashcardQueue {
  static isToday(moment: Date): boolean {
    const now = new Date();

    return (
      moment.getUTCDate() === now.getUTCDate() &&
      moment.getUTCMonth() === now.getUTCMonth() &&
      moment.getUTCFullYear() === now.getUTCFullYear()
    );
  }

  static afterReview(
    cards: readonly Flashcard[],
    result: FlashcardReviewResult,
  ): readonly Flashcard[] {
    const reviewed = cards[0];
    if (reviewed === undefined) return cards;

    const updated: Flashcard = {
      ...reviewed,
      nextReview: result.dueDate,
      fsrsCard: result.newFsrsCard,
    };
    const remaining = [updated, ...cards.slice(1)];

    if (FlashcardQueue.leavesQueue(remaining, result.dueDate)) {
      return remaining.slice(1);
    }

    return FlashcardQueue.sortByDueDate(remaining);
  }

  static sortByDueDate(cards: readonly Flashcard[]): readonly Flashcard[] {
    return [...cards].sort((left, right) => {
      if (left.nextReview === null && right.nextReview === null) return 0;
      if (left.nextReview === null) return -1;
      if (right.nextReview === null) return 1;

      return (
        new Date(left.nextReview).getTime() - new Date(right.nextReview).getTime()
      );
    });
  }

  private static leavesQueue(
    cards: readonly Flashcard[],
    dueDate: string,
  ): boolean {
    const lastReview = cards[cards.length - 1]?.nextReview;

    if (lastReview === undefined || lastReview === null) return true;

    return new Date(dueDate).getTime() >= new Date(lastReview).getTime();
  }
}
