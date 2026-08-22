import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { Money } from "../src/features/settings/money";

const CENTS = fc.integer({ min: 0, max: 100_000_000 });

describe("Money.toDollarText", () => {
  it("toDollarText property always writes exactly two decimals", () => {
    fc.assert(
      fc.property(CENTS, (cents) => {
        expect(Money.toDollarText(cents)).toMatch(/^\d+\.\d{2}$/);
      }),
    );
  });

  it("writes nothing at all for an unset amount", () => {
    expect(Money.toDollarText(null)).toBe("");
  });
});

describe("Money.toAmount", () => {
  it("toAmount property is the dollar text behind a dollar sign", () => {
    fc.assert(
      fc.property(CENTS, (cents) => {
        expect(Money.toAmount(cents)).toBe(`$${Money.toDollarText(cents)}`);
      }),
    );
  });
});

describe("Money.toOptionalCents", () => {
  it("toOptionalCents property round-trips whatever toDollarText wrote", () => {
    fc.assert(
      fc.property(CENTS, (cents) => {
        expect(Money.toOptionalCents(Money.toDollarText(cents))).toBe(cents);
      }),
    );
  });

  it("toOptionalCents property reads blank text as no amount", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[ \t]*$/), (blank) => {
        expect(Money.toOptionalCents(blank)).toBeNull();
      }),
    );
  });

  it("toOptionalCents property refuses a negative amount", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 10_000 }), (dollars) => {
        expect(Money.toOptionalCents(`-${dollars}`)).toBeNull();
      }),
    );
  });

  it("refuses text that is not a number", () => {
    expect(Money.toOptionalCents("twelve")).toBeNull();
  });

  it("rounds a third of a cent to the nearest cent", () => {
    expect(Money.toOptionalCents(" 0.005 ")).toBe(1);
  });
});
