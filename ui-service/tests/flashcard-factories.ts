import fc from "fast-check";
import type {
  BasicFace,
  ClozeFace,
  FeynmanFace,
  Flashcard,
  FlashcardFace,
  ListFace,
} from "../src/features/flashcards/flashcard-models";

const meaningfulText: fc.Arbitrary<string> = fc
  .array(fc.constantFrom("alpha", "beta", "gamma", "delta"), {
    minLength: 1,
    maxLength: 3,
  })
  .map((words) => words.join(" "));

export const basicFace: fc.Arbitrary<BasicFace> = fc.record({
  kind: fc.constant("basic" as const),
  front: fc.string(),
  back: fc.string(),
});

export const clozeFace: fc.Arbitrary<ClozeFace> = fc.record({
  kind: fc.constant("cloze" as const),
  text: fc.string(),
  hiddenParts: fc.array(meaningfulText),
});

export const listFace: fc.Arbitrary<ListFace> = fc.record({
  kind: fc.constant("list" as const),
  question: fc.string(),
  items: fc.array(meaningfulText),
});

export const feynmanFace: fc.Arbitrary<FeynmanFace> = fc.record({
  kind: fc.constant("feynman" as const),
  prompt: fc.string(),
  referenceExplanation: fc.string(),
});

export const anyFace: fc.Arbitrary<FlashcardFace> = fc.oneof(
  basicFace,
  clozeFace,
  listFace,
  feynmanFace,
);

export const dueDate: fc.Arbitrary<string> = fc
  .date({
    min: new Date("2020-01-01"),
    max: new Date("2030-01-01"),
    noInvalidDate: true,
  })
  .map((moment) => moment.toISOString());

export const flashcard: fc.Arbitrary<Flashcard> = fc.record({
  id: fc.uuid(),
  face: anyFace,
  nextReview: fc.option(dueDate, { nil: null }),
  fsrsCard: fc.constant(null),
});

export function cardDue(id: string, nextReview: string | null): Flashcard {
  return {
    id,
    face: { kind: "basic", front: "q", back: "a" },
    nextReview,
    fsrsCard: null,
  };
}
