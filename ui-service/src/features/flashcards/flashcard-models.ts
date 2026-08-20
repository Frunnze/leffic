export type FsrsCard = Readonly<Record<string, unknown>>;

export type FlashcardRating = 1 | 2 | 3 | 4;

export type BasicFace = {
  readonly kind: "basic";
  readonly front: string;
  readonly back: string;
};

export type ClozeFace = {
  readonly kind: "cloze";
  readonly text: string;
  readonly hiddenParts: readonly string[];
};

export type ListFace = {
  readonly kind: "list";
  readonly question: string;
  readonly items: readonly string[];
};

export type FeynmanFace = {
  readonly kind: "feynman";
  readonly prompt: string;
  readonly referenceExplanation: string;
};

export type FlashcardFace = BasicFace | ClozeFace | ListFace | FeynmanFace;

export type Flashcard = {
  readonly id: string;
  readonly face: FlashcardFace;
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
