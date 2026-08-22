import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { FlashcardContent } from "../src/features/flashcards/flashcard-content";
import { anyFace } from "./flashcard-factories";

const KIND_FOR_TYPE: Readonly<Record<string, string>> = {
  cloze: "cloze",
  list: "list",
  feynman: "feynman",
};

describe("FlashcardContent.toFace and FlashcardContent.toContent", () => {
  it("toContent property round-trips through toFace unchanged", () => {
    fc.assert(
      fc.property(anyFace, (face) => {
        const content = FlashcardContent.toContent(face);
        const rebuilt = FlashcardContent.toFace(face.kind, content);

        expect(rebuilt).toEqual(face);
      }),
    );
  });

  it("toFace property gives the kind the type asked for", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("cloze", "list", "feynman", "basic", "other"),
        (type) => {
          const face = FlashcardContent.toFace(type, {});

          expect(face.kind).toBe(KIND_FOR_TYPE[type] ?? "basic");
        },
      ),
    );
  });

  it("toFace property fills every field even from an empty payload", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("cloze", "list", "feynman", "basic"),
        (type) => {
          const face = FlashcardContent.toFace(type, {});

          for (const value of Object.values(face)) {
            expect(value).toBeDefined();
          }
        },
      ),
    );
  });

  it("reads a cloze card out of its stored shape", () => {
    const face = FlashcardContent.toFace("cloze", {
      text: "a b c",
      hidden_parts: ["b"],
    });

    expect(face).toEqual({ kind: "cloze", text: "a b c", hiddenParts: ["b"] });
  });

  it("reads a list card out of its stored shape", () => {
    const face = FlashcardContent.toFace("list", {
      question: "name them",
      items: ["one", "two"],
    });

    expect(face).toEqual({
      kind: "list",
      question: "name them",
      items: ["one", "two"],
    });
  });

  it("reads a feynman card out of its stored shape", () => {
    const face = FlashcardContent.toFace("feynman", {
      prompt: "explain",
      reference_explanation: "because",
    });

    expect(face).toEqual({
      kind: "feynman",
      prompt: "explain",
      referenceExplanation: "because",
    });
  });
});

describe("FlashcardContent.strings", () => {
  it("strings property keeps only non-blank strings", () => {
    fc.assert(
      fc.property(fc.array(fc.oneof(fc.string(), fc.integer())), (raw) => {
        const kept = FlashcardContent.toFace("list", { items: raw });

        for (const item of (kept as { items: readonly string[] }).items) {
          expect(item.trim()).toBe(item);
          expect(item.length).toBeGreaterThan(0);
        }
      }),
    );
  });

  it("reads a non-array as no strings at all", () => {
    const face = FlashcardContent.toFace("list", { items: "nope" });

    expect(face).toEqual({ kind: "list", question: "", items: [] });
  });

  it("drops blank entries and trims the rest", () => {
    const face = FlashcardContent.toFace("cloze", {
      hidden_parts: ["  b  ", "   ", 7],
    });

    expect(face).toEqual({ kind: "cloze", text: "", hiddenParts: ["b"] });
  });
});
