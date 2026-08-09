export type FsrsCard = Readonly<Record<string, unknown>>;

export type FlashcardRating = 1 | 2 | 3 | 4;

export type Flashcard = {
  readonly id: string;
  readonly front: string;
  readonly back: string;
  readonly nextReview: string | null;
  readonly fsrsCard: FsrsCard | null;
};

export type FlashcardDeck = {
  readonly totalFlashcards: number;
  readonly flashcards: readonly Flashcard[];
};

export type RatingIntervals = Readonly<Record<FlashcardRating, number>>;

export type FlashcardReviewResult = {
  readonly dueDate: string;
  readonly newFsrsCard: FsrsCard;
};
