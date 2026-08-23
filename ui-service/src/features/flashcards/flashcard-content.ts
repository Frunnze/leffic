import type { JsonObject } from "../../shared/api/json";
import { FlashcardFaceHandlers } from "./flashcard-face-handlers";
import type { FlashcardFace } from "./flashcard-models";

export class FlashcardContent {
  static toFace(type: string, content: JsonObject): FlashcardFace {
    return FlashcardFaceHandlers.toFace(type, content);
  }

  static toContent(face: FlashcardFace): Readonly<Record<string, unknown>> {
    return FlashcardFaceHandlers.toContent(face);
  }
}
