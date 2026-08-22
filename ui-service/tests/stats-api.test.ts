import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { StatsApi } from "../src/features/folder/stats-api";
import { Session } from "../src/shared/api/session";
import { emptyResponse, jsonResponse, stubFetch } from "./support";

const COUNT = fc.integer({ min: 0, max: 500 });

beforeEach(() => {
  Session.store("token");
});

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});

function statsFor(
  flashcards: unknown,
  testItems: unknown,
  notes: unknown,
): void {
  const fetching = stubFetch();
  const byEndpoint: Readonly<Record<string, unknown>> = {
    "flashcards-stats": flashcards,
    "test-items-stats": testItems,
    "notes-stats": notes,
  };

  fetching.mockImplementation((url: string) => {
    for (const [name, payload] of Object.entries(byEndpoint)) {
      if (url.includes(name)) {
        return Promise.resolve(
          payload === null ? emptyResponse(500) : jsonResponse(payload),
        );
      }
    }

    return Promise.resolve(emptyResponse(404));
  });
}

describe("StatsApi.dueBreakdown", () => {
  it("dueBreakdown property counts today's total as done plus due", async () => {
    await fc.assert(
      fc.asyncProperty(
        COUNT,
        COUNT,
        COUNT,
        async (flashcardsDue, testItemsDue, notesDue) => {
          statsFor(
            { due: flashcardsDue, done: 0 },
            { total: testItemsDue, correct: 0 },
            { due: notesDue, read: 0 },
          );

          const breakdown = await StatsApi.dueBreakdown("home");

          expect(breakdown.totalToday).toBe(
            breakdown.doneToday +
              breakdown.flashcardsDue +
              breakdown.testItemsDue +
              breakdown.notesDue,
          );
        },
      ),
    );
  });

  it("dueBreakdown property adds up everything already done today", async () => {
    await fc.assert(
      fc.asyncProperty(
        COUNT,
        COUNT,
        COUNT,
        async (flashcardsDone, correct, read) => {
          statsFor(
            { due: 0, done: flashcardsDone },
            { total: correct, correct },
            { due: 0, read },
          );

          await expect(StatsApi.dueBreakdown("home")).resolves.toMatchObject({
            doneToday: flashcardsDone + correct + read,
          });
        },
      ),
    );
  });

  it("counts nothing when every endpoint refuses", async () => {
    statsFor(null, null, null);

    await expect(StatsApi.dueBreakdown("home")).resolves.toEqual({
      flashcardsDue: 0,
      testItemsDue: 0,
      notesDue: 0,
      doneToday: 0,
      totalToday: 0,
    });
  });

  it("counts nothing where a payload leaves the numbers out", async () => {
    statsFor({}, {}, {});

    await expect(StatsApi.dueBreakdown("home")).resolves.toMatchObject({
      flashcardsDue: 0,
      testItemsDue: 0,
      notesDue: 0,
    });
  });
});

describe("StatsApi.flashcards and StatsApi.notes", () => {
  it("flashcards property reads the due and done pair straight through", async () => {
    await fc.assert(
      fc.asyncProperty(COUNT, COUNT, async (due, done) => {
        statsFor({ due, done }, { total: 0, correct: 0 }, { due: 0, read: 0 });

        await expect(StatsApi.dueBreakdown("home")).resolves.toMatchObject({
          flashcardsDue: due,
          doneToday: done,
        });
      }),
    );
  });

  it("notes property counts a read note as done today", async () => {
    await fc.assert(
      fc.asyncProperty(COUNT, COUNT, async (due, read) => {
        statsFor({ due: 0, done: 0 }, { total: 0, correct: 0 }, { due, read });

        await expect(StatsApi.dueBreakdown("home")).resolves.toMatchObject({
          notesDue: due,
          doneToday: read,
        });
      }),
    );
  });
});

describe("StatsApi.testItems", () => {
  it("testItems property never reports a negative number due", async () => {
    await fc.assert(
      fc.asyncProperty(COUNT, COUNT, async (total, correct) => {
        statsFor({ due: 0, done: 0 }, { total, correct }, { due: 0, read: 0 });

        const breakdown = await StatsApi.dueBreakdown("home");

        expect(breakdown.testItemsDue).toBeGreaterThanOrEqual(0);
        expect(breakdown.testItemsDue).toBe(Math.max(0, total - correct));
      }),
    );
  });

  it("counts nothing due when the test stats endpoint refuses", async () => {
    statsFor({ due: 1, done: 1 }, null, { due: 1, read: 1 });

    await expect(StatsApi.dueBreakdown("home")).resolves.toMatchObject({
      testItemsDue: 0,
    });
  });
});

describe("StatsApi.readPair and StatsApi.readObject", () => {
  it("readPair property falls back to zero for a missing key", async () => {
    await fc.assert(
      fc.asyncProperty(COUNT, async (due) => {
        statsFor({ due }, { total: 0, correct: 0 }, { due: 0, read: 0 });

        await expect(StatsApi.dueBreakdown("home")).resolves.toMatchObject({
          flashcardsDue: due,
          doneToday: 0,
        });
      }),
    );
  });

  it("readObject property reads nothing out of a refused response", async () => {
    await fc.assert(
      fc.asyncProperty(COUNT, async (due) => {
        statsFor(null, { total: due, correct: 0 }, { due: 0, read: 0 });

        await expect(StatsApi.dueBreakdown("home")).resolves.toMatchObject({
          flashcardsDue: 0,
        });
      }),
    );
  });
});
