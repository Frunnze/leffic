import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { FlashcardWording } from "../src/features/flashcards/flashcard-wording";
import {
  anyFace,
  basicFace,
  clozeFace,
  feynmanFace,
  listFace,
} from "./flashcard-factories";

describe("FlashcardWording.of", () => {
  it("of property always yields a question and an answer", () => {
    fc.assert(
      fc.property(anyFace, (face) => {
        const words = FlashcardWording.of(face);

        expect(typeof words.question).toBe("string");
        expect(typeof words.answer).toBe("string");
      }),
    );
  });

  it("of property asks the front and answers the back of a basic card", () => {
    fc.assert(
      fc.property(basicFace, (face) => {
        expect(FlashcardWording.of(face)).toEqual({
          question: face.front,
          answer: face.back,
        });
      }),
    );
  });

  it("of property names every hidden part in a cloze answer", () => {
    fc.assert(
      fc.property(clozeFace, (face) => {
        const words = FlashcardWording.of(face);

        expect(words.question).toBe(face.text);

        for (const hidden of face.hiddenParts) {
          expect(words.answer).toContain(hidden);
        }
      }),
    );
  });

  it("of property answers a list card with every item", () => {
    fc.assert(
      fc.property(listFace, (face) => {
        expect(FlashcardWording.of(face).answer).toBe(face.items.join(", "));
      }),
    );
  });

  it("of property answers a feynman card with the reference", () => {
    fc.assert(
      fc.property(feynmanFace, (face) => {
        expect(FlashcardWording.of(face)).toEqual({
          question: face.prompt,
          answer: face.referenceExplanation,
        });
      }),
    );
  });
});
