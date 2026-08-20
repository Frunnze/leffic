import { Json, type JsonObject } from "../../shared/api/json";
import type { FlashcardFace } from "./flashcard-models";

export class FlashcardContent {
  static toFace(type: string, content: JsonObject): FlashcardFace {
    if (type === "cloze") {
      return {
        kind: "cloze",
        text: Json.stringOr(content.text, ""),
        hiddenParts: FlashcardContent.strings(content.hidden_parts),
      };
    }

    if (type === "list") {
      return {
        kind: "list",
        question: Json.stringOr(content.question, ""),
        items: FlashcardContent.strings(content.items),
      };
    }

    if (type === "feynman") {
      return {
        kind: "feynman",
        prompt: Json.stringOr(content.prompt, ""),
        referenceExplanation: Json.stringOr(
          content.reference_explanation,
          "",
        ),
      };
    }

    return {
      kind: "basic",
      front: Json.stringOr(content.front, ""),
      back: Json.stringOr(content.back, ""),
    };
  }

  static toContent(face: FlashcardFace): Readonly<Record<string, unknown>> {
    if (face.kind === "cloze") {
      return { text: face.text, hidden_parts: [...face.hiddenParts] };
    }

    if (face.kind === "list") {
      return { question: face.question, items: [...face.items] };
    }

    if (face.kind === "feynman") {
      return {
        prompt: face.prompt,
        reference_explanation: face.referenceExplanation,
      };
    }

    return { front: face.front, back: face.back };
  }

  private static strings(raw: unknown): readonly string[] {
    if (!Array.isArray(raw)) return [];

    return raw
      .filter((entry): entry is string => typeof entry === "string")
      .map((entry) => entry.trim())
      .filter((entry) => entry.length > 0);
  }
}
