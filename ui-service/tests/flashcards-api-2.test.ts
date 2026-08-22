import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { FlashcardsApi } from "../src/features/flashcards/flashcards-api";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";
import "./flashcards-api-support";

describe("FlashcardsApi.remove", () => {
  it("remove property deletes exactly the card it was given", async () => {
    await fc.assert(
      fc.asyncProperty(fc.uuid(), async (flashcardId) => {
        const fetching = stubFetch(jsonResponse({}));

        await FlashcardsApi.remove(flashcardId);

        expect(requestedUrl(fetching)).toContain(`flashcard_id=${flashcardId}`);
        expect(requestedInit(fetching).method).toBe("DELETE");
      }),
    );
  });
});
