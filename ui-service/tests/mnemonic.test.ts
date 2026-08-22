import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { MnemonicPrompt } from "../src/features/flashcards/mnemonic-prompt";
import { MnemonicRequest } from "../src/features/flashcards/mnemonic-request";
import { cardDue } from "./flashcard-factories";

const SHOWN_LIMIT = 60;

describe("MnemonicPrompt.forCard", () => {
  it("forCard property carries both sides of the card into the prompt", () => {
    fc.assert(
      fc.property(fc.string(), fc.string(), (front, back) => {
        const prompt = MnemonicPrompt.forCard(front, back);

        expect(prompt).toContain(`Flashcard question: ${front}`);
        expect(prompt).toContain(`Flashcard answer: ${back}`);
      }),
    );
  });

  it("forCard property always names every labelled section", () => {
    fc.assert(
      fc.property(fc.string(), fc.string(), (front, back) => {
        const prompt = MnemonicPrompt.forCard(front, back);

        for (const section of [
          "ROLE",
          "TASK",
          "CONTEXT",
          "CONSTRAINTS",
          "OUTPUT",
        ]) {
          expect(prompt).toContain(section);
        }
      }),
    );
  });
});

describe("MnemonicPrompt.shownFor", () => {
  it("shownFor property shows a short question whole", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[A-Za-z ]{0,60}$/), (front) => {
        expect(MnemonicPrompt.shownFor(front)).toBe(
          `Mnemonic for: ${front.trim()}`,
        );
      }),
    );
  });

  it("shownFor property ends a long question with an ellipsis", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[A-Za-z]{61,90}$/), (front) => {
        const shown = MnemonicPrompt.shownFor(front);

        expect(shown.endsWith("…")).toBe(true);
        expect(shown.length).toBeLessThanOrEqual(
          "Mnemonic for: ".length + SHOWN_LIMIT + 1,
        );
      }),
    );
  });

  it("trims the trailing space before the ellipsis", () => {
    const front = `${"a".repeat(SHOWN_LIMIT - 1)}   tail`;

    expect(MnemonicPrompt.shownFor(front)).toBe(
      `Mnemonic for: ${"a".repeat(SHOWN_LIMIT - 1)}…`,
    );
  });
});

describe("MnemonicRequest.forCard", () => {
  it("forCard property asks about the card's own wording", () => {
    fc.assert(
      fc.property(fc.string(), fc.string(), (front, back) => {
        const card = cardDue("id", null);
        const asked = MnemonicRequest.forCard({
          ...card,
          face: { kind: "basic", front, back },
        });

        expect(asked.question).toContain(`Flashcard question: ${front}`);
        expect(asked.shownAs).toContain("Mnemonic for:");
      }),
    );
  });
});
