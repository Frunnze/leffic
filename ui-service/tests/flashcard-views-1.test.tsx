import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { ClozeText } from "../src/features/flashcards/ClozeText";
import { FaceView } from "../src/features/flashcards/FaceView";
import {
  FlashcardAnswer,
  FlashcardPrompt,
} from "../src/features/flashcards/FlashcardPrompt";
import {
  FlashcardTextArea,
} from "../src/features/flashcards/FlashcardTextArea";
import { BASIC, CLOZE, FEYNMAN, LIST } from "./flashcard-views-support";

describe("ClozeText", () => {
  it("blanks out a hidden part until it is revealed", () => {
    fc.assert(
      fc.property(fc.boolean(), (isRevealed) => {
        const { unmount } = render(() => (
          <ClozeText
            text="a big secret"
            hiddenParts={["big"]}
            isRevealed={isRevealed}
          />
        ));
        const blank = document.querySelector(".cloze-blank");

        const shown = blank?.textContent ?? "";

        expect(shown).toHaveLength(3);
        expect(shown.trim()).toBe(isRevealed ? "big" : "");
        unmount();
      }),
    );
  });

  it("marks a revealed blank as revealed", () => {
    render(() => (
      <ClozeText text="a big secret" hiddenParts={["big"]} isRevealed />
    ));

    expect(document.querySelector(".cloze-blank")?.className).toContain(
      "is-revealed",
    );
  });

  it("shows the plain pieces around the blank", () => {
    render(() => (
      <ClozeText text="a big secret" hiddenParts={["big"]} isRevealed={false} />
    ));

    expect(
      [...document.querySelectorAll("span")].map((piece) => piece.textContent),
    ).toEqual(["a ", " secret"]);
  });
});

describe("FaceView", () => {
  it("shows the arm that belongs to the face it was given", () => {
    fc.assert(
      fc.property(fc.constantFrom(BASIC, CLOZE, LIST, FEYNMAN), (face) => {
        const { unmount } = render(() => (
          <FaceView
            face={face}
            render={(selected) => <p>{selected.kind}</p>}
          />
        ));

        expect(document.body.textContent).toBe(face.kind);
        unmount();
      }),
    );
  });
});

describe("FlashcardPrompt", () => {
  it("prompt property renders every face", () => {
    fc.assert(
      fc.property(fc.constantFrom(BASIC, CLOZE, LIST, FEYNMAN), (face) => {
        const shown = render(() => <FlashcardPrompt face={face} />);

        expect(shown.container.textContent).not.toBe("");
        shown.unmount();
      }),
    );
  });

  it("asks the front of a basic card", () => {
    render(() => <FlashcardPrompt face={BASIC} />);

    expect(document.body.textContent).toContain("Front");
  });

  it("blanks the hidden part of a cloze card", () => {
    render(() => <FlashcardPrompt face={CLOZE} />);

    expect(document.querySelector(".cloze-blank")?.textContent.trim()).toBe(
      "",
    );
  });

  it("says how many items a list card wants", () => {
    render(() => <FlashcardPrompt face={LIST} />);

    expect(document.body.textContent).toContain("Name 2 items");
  });

  it("shows no extra flip hint on a feynman card", () => {
    render(() => <FlashcardPrompt face={FEYNMAN} />);

    expect(document.body.textContent).toBe("Explain gravity");
  });
});

describe("FlashcardAnswer", () => {
  it("answer property renders every face", () => {
    fc.assert(
      fc.property(fc.constantFrom(BASIC, CLOZE, LIST, FEYNMAN), (face) => {
        const shown = render(() => <FlashcardAnswer face={face} />);

        expect(shown.container.textContent).not.toBe("");
        shown.unmount();
      }),
    );
  });

  it("answers a basic card with its back", () => {
    render(() => <FlashcardAnswer face={BASIC} />);

    expect(document.body.textContent).toContain("Back");
  });

  it("reveals the hidden part of a cloze card", () => {
    render(() => <FlashcardAnswer face={CLOZE} />);

    expect(document.querySelector(".cloze-blank")?.textContent).toBe("big");
  });

  it("answers a list card with every item", () => {
    render(() => <FlashcardAnswer face={LIST} />);

    expect(
      [...document.querySelectorAll("li")].map((item) => item.textContent),
    ).toEqual(["one", "two"]);
  });

  it("answers a feynman card with the reference explanation", () => {
    render(() => <FlashcardAnswer face={FEYNMAN} />);

    expect(document.body.textContent).toContain("Mass bends spacetime");
  });
});

describe("FlashcardTextArea", () => {
  it("reports whatever is typed into it", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[A-Za-z ]{1,12}$/), (typed) => {
        const onInput = vi.fn();
        const { unmount } = render(() => (
          <FlashcardTextArea
            id="field"
            label="Field"
            rows={2}
            value=""
            onInput={onInput}
          />
        ));

        fireEvent.input(screen.getByLabelText("Field"), {
          target: { value: typed },
        });

        expect(onInput).toHaveBeenCalledWith(typed);
        unmount();
      }),
    );
  });
});
