import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { AssessmentApi } from "../src/features/assessment/assessment-api";
import { emptyResponse, jsonResponse, stubFetch } from "./support";
import "./assessment-api-support";

describe("AssessmentApi.sessionResult", () => {
  it("sessionResult property counts however many were correct", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 0, max: 100 }), async (correct) => {
        stubFetch(jsonResponse({ correct }));

        await expect(AssessmentApi.sessionResult("s")).resolves.toEqual({
          correct,
        });
      }),
    );
  });

  it("reports nothing when the session cannot be read", async () => {
    stubFetch(emptyResponse(404));

    await expect(AssessmentApi.sessionResult("s")).resolves.toBeNull();
  });

  it("counts nothing when the payload leaves the number out", async () => {
    stubFetch(jsonResponse({}));

    await expect(AssessmentApi.sessionResult("s")).resolves.toEqual({
      correct: 0,
    });
  });
});
