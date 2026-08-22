import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { FlashcardsApi } from "../src/features/flashcards/flashcards-api";
import {
  emptyResponse,
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";
import { anyFace } from "./flashcard-factories";
import { RATING, SCOPE, storedCard } from "./flashcards-api-support";

describe("FlashcardsApi.deck", () => {
  it("deck property asks for the scope it was given", async () => {
    await fc.assert(
      fc.asyncProperty(SCOPE, fc.uuid(), async (scope, scopeId) => {
        const fetching = stubFetch(
          jsonResponse({ total_flashcards: 1, flashcards: [storedCard()] }),
        );

        await FlashcardsApi.deck(scope, scopeId);

        expect(requestedUrl(fetching)).toContain(
          `${scope}_id=${encodeURIComponent(scopeId)}`,
        );
      }),
    );
  });

  it("deck property reports as many cards as the service listed", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 40 }), async (total) => {
        const flashcards = Array.from({ length: total }, (_, index) =>
          storedCard({ id: index }),
        );
        stubFetch(jsonResponse({ total_flashcards: total, flashcards }));

        const deck = await FlashcardsApi.deck("folder", "home");

        expect(deck?.totalFlashcards).toBe(total);
        expect(deck?.flashcards).toHaveLength(total);
      }),
    );
  });

  it("reports no deck when the service refuses", async () => {
    stubFetch(emptyResponse(404));

    await expect(FlashcardsApi.deck("folder", "home")).resolves.toBeNull();
  });

  it("reports no deck when nothing is due", async () => {
    stubFetch(jsonResponse({ total_flashcards: 0, flashcards: [] }));

    await expect(FlashcardsApi.deck("folder", "home")).resolves.toBeNull();
  });
});

describe("FlashcardsApi.toFlashcard", () => {
  it("toFlashcard property reads back whatever face was stored", async () => {
    await fc.assert(
      fc.asyncProperty(anyFace, async (face) => {
        const { FlashcardContent } =
          await import("../src/features/flashcards/flashcard-content");
        stubFetch(
          jsonResponse({
            total_flashcards: 1,
            flashcards: [
              storedCard({
                type: face.kind,
                content: FlashcardContent.toContent(face),
              }),
            ],
          }),
        );

        const deck = await FlashcardsApi.deck("folder", "home");

        expect(deck?.flashcards[0]?.face).toEqual(face);
      }),
    );
  });

  it("fills in what a sparse card leaves out", async () => {
    stubFetch(
      jsonResponse({
        total_flashcards: 1,
        flashcards: [{ id: 8, content: {} }],
      }),
    );

    const deck = await FlashcardsApi.deck("folder", "home");

    expect(deck?.flashcards[0]).toEqual({
      id: "8",
      face: { kind: "basic", front: "", back: "" },
      nextReview: null,
      fsrsCard: null,
    });
  });

  it("reads the schedule a card already carries", async () => {
    stubFetch(
      jsonResponse({
        total_flashcards: 1,
        flashcards: [
          storedCard({ next_review: "2024-02-02", fsrs_card: { step: 1 } }),
        ],
      }),
    );

    const deck = await FlashcardsApi.deck("folder", "home");

    expect(deck?.flashcards[0]).toMatchObject({
      nextReview: "2024-02-02",
      fsrsCard: { step: 1 },
    });
  });
});

describe("FlashcardsApi.ratingIntervals", () => {
  it("ratingIntervals property answers with all four ratings", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 0, max: 10_000 }), async (seconds) => {
        stubFetch(
          jsonResponse({ 1: seconds, 2: seconds, 3: seconds, 4: seconds }),
        );

        await expect(FlashcardsApi.ratingIntervals(null)).resolves.toEqual({
          1: seconds,
          2: seconds,
          3: seconds,
          4: seconds,
        });
      }),
    );
  });

  it("reports no intervals when the service refuses", async () => {
    stubFetch(emptyResponse(500));

    await expect(FlashcardsApi.ratingIntervals({})).resolves.toBeNull();
  });

  it("counts a missing interval as none at all", async () => {
    stubFetch(jsonResponse({}));

    await expect(FlashcardsApi.ratingIntervals(null)).resolves.toEqual({
      1: 0,
      2: 0,
      3: 0,
      4: 0,
    });
  });
});

describe("FlashcardsApi.review", () => {
  it("review property posts the card and its rating together", async () => {
    await fc.assert(
      fc.asyncProperty(fc.uuid(), RATING, async (flashcardId, rating) => {
        const fetching = stubFetch(
          jsonResponse({ due_date: "2024-03-03", new_fsrs_card: {} }),
        );

        await FlashcardsApi.review(flashcardId, rating);

        expect(requestedInit(fetching).body).toBe(
          JSON.stringify({ flashcard_id: flashcardId, rating }),
        );
      }),
    );
  });

  it("reads the new schedule out of the reply", async () => {
    stubFetch(
      jsonResponse({ due_date: "2024-03-03", new_fsrs_card: { step: 2 } }),
    );

    await expect(FlashcardsApi.review("1", 3)).resolves.toEqual({
      dueDate: "2024-03-03",
      newFsrsCard: { step: 2 },
    });
  });
});
