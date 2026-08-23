import {
  FlashcardFaceHandlers,
  type FlashcardWords,
} from "./flashcard-face-handlers";
import type { FlashcardFace } from "./flashcard-models";

export class FlashcardWording {
  static of(face: FlashcardFace): FlashcardWords {
    return FlashcardFaceHandlers.of(face);
  }
}
