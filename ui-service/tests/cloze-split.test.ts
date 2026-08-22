import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { ClozeSplit } from "../src/features/flashcards/cloze-split";

const WORD = fc
  .string({ minLength: 1, maxLength: 6 })
  .filter((word) => word.trim().length > 0);

describe("ClozeSplit.pieces", () => {
  it("pieces property rebuilds the original text when joined back up", () => {
    fc.assert(
      fc.property(
        fc.string(),
        fc.array(WORD, { maxLength: 3 }),
        (text, hiddenParts) => {
          const rebuilt = ClozeSplit.pieces(text, hiddenParts)
            .map((piece) => piece.text)
            .join("");

          expect(rebuilt).toBe(text);
        },
      ),
    );
  });

  it("pieces property never keeps an empty piece", () => {
    fc.assert(
      fc.property(
        fc.string(),
        fc.array(WORD, { maxLength: 3 }),
        (text, hiddenParts) => {
          const pieces = ClozeSplit.pieces(text, hiddenParts);

          expect(pieces.every((piece) => piece.text.length > 0)).toBe(true);
        },
      ),
    );
  });

  it("pieces property hides every occurrence of a hidden part", () => {
    fc.assert(
      fc.property(WORD, fc.string(), (hidden, around) => {
        const text = `${around}${hidden}${around}${hidden}${around}`;
        const pieces = ClozeSplit.pieces(text, [hidden]);
        const occurrences = text.split(hidden).length - 1;

        expect(pieces.filter((piece) => piece.isHidden)).toHaveLength(
          occurrences,
        );
      }),
    );
  });

  it("leaves text with nothing hidden as a single visible piece", () => {
    expect(ClozeSplit.pieces("plain sentence", [])).toEqual([
      { text: "plain sentence", isHidden: false },
    ]);
  });

  it("does not hide inside an already hidden piece", () => {
    const pieces = ClozeSplit.pieces("alpha beta", ["alpha", "lph"]);

    expect(pieces).toEqual([
      { text: "alpha", isHidden: true },
      { text: " beta", isHidden: false },
    ]);
  });
});

describe("ClozeSplit.hideEverywhere and ClozeSplit.hideInside", () => {
  it("hideEverywhere property leaves already hidden pieces alone", () => {
    fc.assert(
      fc.property(WORD, WORD, (first, second) => {
        const pieces = ClozeSplit.pieces(`${first}${second}`, [first, second]);
        const hidden = pieces.filter((piece) => piece.isHidden);

        expect(hidden.length).toBeGreaterThan(0);
      }),
    );
  });

  it("hideInside property splits a text around each occurrence", () => {
    fc.assert(
      fc.property(WORD, (hidden) => {
        const pieces = ClozeSplit.pieces(hidden, [hidden]);

        expect(pieces).toEqual([{ text: hidden, isHidden: true }]);
      }),
    );
  });
});
