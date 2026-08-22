import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { GenerationApi } from "../src/features/folder/import/generation-api";
import { jsonResponse, requestedUrl, stubFetch } from "./support";
import { ORIGIN, sentBody } from "./generation-api-support";

describe("GenerationApi.wishBody", () => {
  it("wishBody property carries the wanted flashcard amount through", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 50 }),
        async (flashcardAmount) => {
          const fetching = stubFetch(jsonResponse({}));

          await GenerationApi.start(
            { kind: "topic", topic: "x" },
            ORIGIN,
            "home",
            {
              flashcardTypes: ["basic"],
              flashcardAmount,
              testTypes: [],
              testAmount: undefined,
              note: false,
            },
          );

          expect(sentBody(fetching)).toMatchObject({
            flashcards: { types: ["basic"], amount: flashcardAmount },
          });
        },
      ),
    );
  });

  it("asks for everything by default", async () => {
    const fetching = stubFetch(jsonResponse({}));

    await GenerationApi.start({ kind: "topic", topic: "x" }, ORIGIN, "home");

    expect(sentBody(fetching)).toMatchObject({
      note: {},
      flashcards: { types: ["basic"], amount: null },
      test: { types: ["multiple_choice"] },
    });
  });

  it("asks for nothing that was not wanted", async () => {
    const fetching = stubFetch(jsonResponse({}));

    await GenerationApi.start({ kind: "topic", topic: "x" }, ORIGIN, "home", {
      flashcardTypes: [],
      flashcardAmount: null,
      testTypes: [],
      testAmount: undefined,
      note: false,
    });

    expect(sentBody(fetching)).toMatchObject({ folder_id: "home" });
    expect(sentBody(fetching)).not.toHaveProperty("note");
    expect(sentBody(fetching)).not.toHaveProperty("flashcards");
    expect(sentBody(fetching)).not.toHaveProperty("test");
  });

  it("names the test amount only when one was asked for", async () => {
    const fetching = stubFetch(jsonResponse({}));

    await GenerationApi.start({ kind: "topic", topic: "x" }, ORIGIN, "home", {
      flashcardTypes: [],
      flashcardAmount: null,
      testTypes: ["short_answer"],
      testAmount: 7,
      note: false,
    });

    expect(sentBody(fetching)).toMatchObject({
      test: { types: ["short_answer"], amount: 7 },
    });
  });
});

describe("GenerationApi.progress, toStatus and toGeneratedUnit", () => {
  it("progress property asks the endpoint that belongs to the kind", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom("flashcards", "note", "test" as const),
        async (kind) => {
          const fetching = stubFetch(jsonResponse({ status: "PENDING" }));

          await GenerationApi.progress(kind, "task-1");

          expect(requestedUrl(fetching)).toContain("task-1");
        },
      ),
    );
  });

  it("toStatus property reads anything it does not know as pending", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string().filter((name) => name !== "SUCCESS" && name !== "FAILURE"),
        async (status) => {
          stubFetch(jsonResponse({ status }));

          await expect(GenerationApi.progress("note", "t")).resolves.toEqual({
            status: "PENDING",
            unit: null,
          });
        },
      ),
    );
  });

  it("reports a failure without a unit", async () => {
    stubFetch(jsonResponse({ status: "FAILURE" }));

    await expect(GenerationApi.progress("test", "t")).resolves.toEqual({
      status: "FAILURE",
      unit: null,
    });
  });

  it("reads the finished unit out of a success", async () => {
    stubFetch(
      jsonResponse({
        status: "SUCCESS",
        note_id: 3,
        name: "Cells",
        type: "note",
        created_at: "2024-01-01T00:00:00.000Z",
      }),
    );

    const progress = await GenerationApi.progress("note", "t");

    expect(progress.unit).toMatchObject({
      id: "3",
      name: "Cells",
      type: "note",
    });
  });

  it("reports a success with no unit when the id is missing", async () => {
    stubFetch(jsonResponse({ status: "SUCCESS" }));

    await expect(GenerationApi.progress("flashcards", "t")).resolves.toEqual({
      status: "SUCCESS",
      unit: null,
    });
  });
});

describe("GenerationApi.toGeneratedUnit", () => {
  it("toGeneratedUnit property reads the id field its kind writes", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom(
          ["flashcards", "flashcard_deck_id"],
          ["note", "note_id"],
          ["test", "test_id"],
        ),
        async ([kind, idField]) => {
          stubFetch(
            jsonResponse({
              status: "SUCCESS",
              [idField]: 11,
              name: "Made",
              type: kind === "flashcards" ? "flashcard_deck" : kind,
              created_at: "2024-01-01T00:00:00.000Z",
            }),
          );

          const progress = await GenerationApi.progress(
            kind as "flashcards" | "note" | "test",
            "t",
          );

          expect(progress.unit).toMatchObject({ id: "11", name: "Made" });
        },
      ),
    );
  });
});
