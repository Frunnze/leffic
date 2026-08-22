import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { AssessmentApi } from "../src/features/assessment/assessment-api";
import { jsonResponse, requestedInit, stubFetch } from "./support";
import "./assessment-api-support";

describe("AssessmentApi.updateItem", () => {
  it("updateItem property sends the edited question as one patch", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 999 }),
        fc.string(),
        fc.string(),
        async (testItemId, question, correctAnswer) => {
          const fetching = stubFetch(jsonResponse({}));

          await AssessmentApi.updateItem(String(testItemId), {
            question,
            correctAnswer,
            wrongAnswers: ["a"],
          });

          expect(requestedInit(fetching).method).toBe("PATCH");
          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({
              test_item_id: testItemId,
              content: {
                question,
                true_option: correctAnswer,
                false_options: ["a"],
              },
            }),
          );
        },
      ),
    );
  });
});
