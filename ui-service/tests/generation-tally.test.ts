import { describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import {
  GenerationTally,
  type GenerationOutcome,
} from "../src/features/folder/import/generation-tally";
import { unitOf } from "./unit-factories";

function outcome(succeeded: boolean): GenerationOutcome {
  return { kind: "flashcards", succeeded, units: [] };
}

describe("GenerationTally.record", () => {
  it("record property reports only once every awaited job is in", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 8 }), (jobCount) => {
        const report = vi.fn();
        const tally = new GenerationTally("flashcards", jobCount, report);

        for (let done = 0; done < jobCount; done += 1) {
          expect(report).not.toHaveBeenCalled();
          tally.record(outcome(true));
        }

        expect(report).toHaveBeenCalledTimes(1);
      }),
    );
  });

  it("record property succeeds only when every job succeeded", () => {
    fc.assert(
      fc.property(
        fc.array(fc.boolean(), { minLength: 1, maxLength: 6 }),
        (outcomes) => {
          const report = vi.fn();
          const tally = new GenerationTally(
            "flashcards",
            outcomes.length,
            report,
          );

          for (const succeeded of outcomes) tally.record(outcome(succeeded));

          expect(report).toHaveBeenCalledWith(
            expect.objectContaining({ succeeded: outcomes.every(Boolean) }),
          );
        },
      ),
    );
  });

  it("reports the unit a job produced", () => {
    const report = vi.fn();
    const made = unitOf({ id: "made" });
    const tally = new GenerationTally("note", 2, report);

    tally.record({ kind: "note", succeeded: true, units: [] });
    tally.record({ kind: "note", succeeded: true, units: [made] });

    expect(report).toHaveBeenCalledWith({
      kind: "note",
      succeeded: true,
      units: [made],
    });
  });
});
