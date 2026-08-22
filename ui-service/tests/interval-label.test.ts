import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { IntervalLabel } from "../src/features/flashcards/interval-label";

const UNITS = ["s", "min", "h", "days", "mo", "y"];

describe("IntervalLabel.fromSeconds", () => {
  it("fromSeconds property always names a whole count and a unit", () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 4_000_000_000 }), (seconds) => {
        const label = IntervalLabel.fromSeconds(seconds);
        const [count, unit] = label.split(" ");

        expect(Number.isInteger(Number(count))).toBe(true);
        expect(UNITS).toContain(unit);
      }),
    );
  });

  it("fromSeconds property never counts higher than the raw seconds", () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 4_000_000_000 }), (seconds) => {
        const count = Number(IntervalLabel.fromSeconds(seconds).split(" ")[0]);

        expect(count).toBeLessThanOrEqual(Math.max(seconds, 1));
      }),
    );
  });

  it.each([
    [30, "30 s"],
    [59, "59 s"],
    [60, "1 min"],
    [3599, "59 min"],
    [3600, "1 h"],
    [86399, "23 h"],
    [86400, "1 days"],
    [2591999, "29 days"],
    [2592000, "1 mo"],
    [31535999, "12 mo"],
    [31536000, "1 y"],
  ])("reads %i seconds as %s", (seconds, label) => {
    expect(IntervalLabel.fromSeconds(seconds)).toBe(label);
  });
});
