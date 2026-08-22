import { beforeEach, describe, expect, it } from "vitest";
import fc from "fast-check";
import {
  AssessmentProgress,
} from "../src/features/assessment/assessment-progress";

const SCOPE = fc.uuid();

beforeEach(() => {
  localStorage.clear();
});

describe("AssessmentProgress.remember, storedPage and storedIndex", () => {
  it("remember property is read back exactly by storedPage and storedIndex", () => {
    fc.assert(
      fc.property(
        SCOPE,
        fc.integer({ min: 1, max: 500 }),
        fc.integer({ min: 0, max: 50 }),
        (scopeId, page, index) => {
          AssessmentProgress.remember(scopeId, page, index);

          expect(AssessmentProgress.storedPage(scopeId)).toBe(page);
          expect(AssessmentProgress.storedIndex(scopeId)).toBe(index);
        },
      ),
    );
  });

  it("storedPage property starts every unseen test on page one", () => {
    fc.assert(
      fc.property(SCOPE, (scopeId) => {
        expect(AssessmentProgress.storedPage(scopeId)).toBe(1);
      }),
    );
  });

  it("storedIndex property starts every unseen test at the first item", () => {
    fc.assert(
      fc.property(SCOPE, (scopeId) => {
        expect(AssessmentProgress.storedIndex(scopeId)).toBe(0);
      }),
    );
  });
});

describe("AssessmentProgress.forget", () => {
  it("forget property puts a test back to its starting position", () => {
    fc.assert(
      fc.property(SCOPE, fc.integer({ min: 2, max: 9 }), (scopeId, page) => {
        AssessmentProgress.remember(scopeId, page, page);
        AssessmentProgress.forget(scopeId);

        expect(AssessmentProgress.storedPage(scopeId)).toBe(1);
        expect(AssessmentProgress.storedIndex(scopeId)).toBe(0);
      }),
    );
  });
});

describe("AssessmentProgress.readNumber", () => {
  it("readNumber property falls back when the stored text is not a number", () => {
    fc.assert(
      fc.property(SCOPE, (scopeId) => {
        localStorage.setItem(`testPage${scopeId}`, "not a number");

        expect(AssessmentProgress.storedPage(scopeId)).toBe(1);
      }),
    );
  });
});

describe("AssessmentProgress.overallPosition", () => {
  it("overallPosition property counts from one and never repeats a number", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 20 }),
        fc.integer({ min: 1, max: 20 }),
        fc.integer({ min: 0, max: 19 }),
        (page, perPage, index) => {
          const position = AssessmentProgress.overallPosition(
            page,
            perPage,
            index,
          );

          expect(position).toBeGreaterThanOrEqual(1);
          expect(position).toBe((page - 1) * perPage + index + 1);
        },
      ),
    );
  });

  it("numbers the first item of the first page as one", () => {
    expect(AssessmentProgress.overallPosition(1, 10, 0)).toBe(1);
  });
});

describe("AssessmentProgress.optionLetter", () => {
  it("optionLetter property gives a single capital letter for a real option", () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 7 }), (index) => {
        expect(AssessmentProgress.optionLetter(index)).toMatch(/^[A-H]$/);
      }),
    );
  });

  it("optionLetter property falls back to a number past the alphabet", () => {
    fc.assert(
      fc.property(fc.integer({ min: 8, max: 40 }), (index) => {
        expect(AssessmentProgress.optionLetter(index)).toBe(String(index + 1));
      }),
    );
  });
});
