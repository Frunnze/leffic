import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { AssessmentApi } from "../src/features/assessment/assessment-api";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";
import { SCOPE, storedItem } from "./assessment-api-support";

describe("AssessmentApi.page", () => {
  it("page property asks for the scope and page it was given", async () => {
    await fc.assert(
      fc.asyncProperty(
        SCOPE,
        fc.uuid(),
        fc.integer({ min: 1, max: 40 }),
        async (scope, scopeId, page) => {
          const fetching = stubFetch(jsonResponse({ test_items: [] }));

          await AssessmentApi.page(scope, scopeId, page);

          expect(requestedUrl(fetching)).toContain(
            `${scope}_id=${encodeURIComponent(scopeId)}`,
          );
          expect(requestedUrl(fetching)).toContain(`page=${page}`);
        },
      ),
    );
  });

  it("page property keeps the page it asked for when none comes back", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 40 }), async (page) => {
        stubFetch(jsonResponse({ test_items: [] }));

        await expect(AssessmentApi.page("test", "1", page)).resolves.toEqual({
          testSession: "",
          items: [],
          page,
          perPage: 10,
          totalItems: 0,
        });
      }),
    );
  });

  it("reads the page the service reported", async () => {
    stubFetch(
      jsonResponse({
        test_items: [],
        test_session: "session-1",
        page: 3,
        per_page: 5,
        total_items: 12,
      }),
    );

    await expect(AssessmentApi.page("test", "1", 1)).resolves.toMatchObject({
      testSession: "session-1",
      page: 3,
      perPage: 5,
      totalItems: 12,
    });
  });
});

describe("AssessmentApi.toItem, toOption and toAnswers", () => {
  it("toItem property always asks a question, even a missing one", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), async (question) => {
        stubFetch(
          jsonResponse({
            test_items: [
              storedItem({ content: { question, shuffled_options: [] } }),
            ],
          }),
        );

        const page = await AssessmentApi.page("test", "1", 1);

        expect(page.items[0]?.question).toBe(question);
      }),
    );
  });

  it("toAnswers property keeps only answers a test item can carry", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(fc.oneof(fc.integer(), fc.string(), fc.boolean())),
        async (lastAnswers) => {
          stubFetch(
            jsonResponse({
              test_items: [storedItem({ last_answers: lastAnswers })],
            }),
          );

          const page = await AssessmentApi.page("test", "1", 1);

          for (const answer of page.items[0]?.lastAnswers ?? []) {
            expect(["number", "string"]).toContain(typeof answer);
          }
        },
      ),
    );
  });

  it("toOption property reads an option's number and wording", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer(), fc.string(), async (id, option) => {
        stubFetch(
          jsonResponse({
            test_items: [
              storedItem({
                content: { question: "q", shuffled_options: [{ id, option }] },
              }),
            ],
          }),
        );

        const page = await AssessmentApi.page("test", "1", 1);

        expect(page.items[0]?.options).toEqual([{ id, option }]);
      }),
    );
  });

  it("fills in what a sparse item leaves out", async () => {
    stubFetch(
      jsonResponse({
        test_items: [{ id: 5, content: { shuffled_options: [] } }],
      }),
    );

    const page = await AssessmentApi.page("test", "1", 1);

    expect(page.items[0]).toEqual({
      id: "5",
      type: "multiple_choice",
      question: "",
      options: [],
      lastAnswers: [],
    });
  });

  it("reads no answers out of a payload that carries none", async () => {
    stubFetch(
      jsonResponse({ test_items: [storedItem({ last_answers: "nope" })] }),
    );

    const page = await AssessmentApi.page("test", "1", 1);

    expect(page.items[0]?.lastAnswers).toEqual([]);
  });
});

describe("AssessmentApi.submitAnswer", () => {
  it("submitAnswer property posts the whole answer to the review endpoint", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.uuid(),
        fc.uuid(),
        fc.array(fc.integer()),
        async (testItemId, testSession, answers) => {
          const fetching = stubFetch(jsonResponse({}));

          await AssessmentApi.submitAnswer(testItemId, testSession, answers);

          expect(requestedUrl(fetching)).toContain(
            "/api/content/review-test-item",
          );
          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({
              test_item_id: testItemId,
              test_session: testSession,
              answers,
            }),
          );
        },
      ),
    );
  });
});
