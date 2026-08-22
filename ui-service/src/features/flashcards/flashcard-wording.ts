import type { FlashcardFace } from "./flashcard-models";

type FlashcardWords = {
  readonly question: string;
  readonly answer: string;
};

export class FlashcardWording {
  static of(face: FlashcardFace): FlashcardWords {
    if (face.kind === "cloze") {
      return {
        question: face.text,
        answer: `The hidden parts are: ${face.hiddenParts.join(", ")}`,
      };
    }

    if (face.kind === "list") {
      return {
        question: face.question,
        answer: face.items.join(", "),
      };
    }

    if (face.kind === "feynman") {
      return { question: face.prompt, answer: face.referenceExplanation };
    }

    return { question: face.front, answer: face.back };
  }
}
