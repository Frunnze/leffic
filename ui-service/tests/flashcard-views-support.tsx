import type {
  FlashcardFace,
} from "../src/features/flashcards/flashcard-models";

export const BASIC: FlashcardFace = {
  kind: "basic",
  front: "Front",
  back: "Back",
};
export const CLOZE: FlashcardFace = {
  kind: "cloze",
  text: "a big secret",
  hiddenParts: ["big"],
};
export const LIST: FlashcardFace = {
  kind: "list",
  question: "Name them",
  items: ["one", "two"],
};
export const FEYNMAN: FlashcardFace = {
  kind: "feynman",
  prompt: "Explain gravity",
  referenceExplanation: "Mass bends spacetime",
};
