import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { FlashcardsApi } from "../src/features/flashcards/flashcards-api";
import { jsonResponse, requestedInit, stubFetch } from "./support";
import { anyFace } from "./flashcard-factories";
import "./flashcards-api-support";

describe("FlashcardsApi.update", () => {
  it("update property sends the edited face as one patch", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 999 }),
        anyFace,
        async (flashcardId, face) => {
          const { FlashcardContent } =
            await import("../src/features/flashcards/flashcard-content");
          const fetching = stubFetch(jsonResponse({}));

          await FlashcardsApi.update(String(flashcardId), face);

          expect(requestedInit(fetching).method).toBe("PATCH");
          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({
              flashcard_id: flashcardId,
              content: FlashcardContent.toContent(face),
            }),
          );
        },
      ),
    );
  });
});
