import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { ConfirmDialog } from "../src/features/flashcards/ConfirmDialog";
import { FlashcardFields } from "../src/features/flashcards/FlashcardFields";
import { FlashcardRatings } from "../src/features/flashcards/FlashcardRatings";
import { BASIC, CLOZE, FEYNMAN, LIST } from "./flashcard-views-support";

describe("FlashcardFields", () => {
  it("fields property exposes editable fields for every face", () => {
    fc.assert(
      fc.property(fc.constantFrom(BASIC, CLOZE, LIST, FEYNMAN), (face) => {
        const shown = render(() => (
          <FlashcardFields face={face} onChange={vi.fn()} />
        ));

        expect(shown.container.querySelectorAll("textarea").length).toBe(2);
        shown.unmount();
      }),
    );
  });

  it.each([
    [BASIC, ["Front", "Back"]],
    [CLOZE, ["Sentence", "Hidden parts, one per line"]],
    [LIST, ["Question", "Items, one per line"]],
    [FEYNMAN, ["Explain this", "Reference explanation"]],
  ] as const)("edits every field of a %s card", (face, labels) => {
    render(() => <FlashcardFields face={face} onChange={vi.fn()} />);

    for (const label of labels) {
      expect(screen.getByLabelText(label)).toBeTruthy();
    }
  });

  it.each([
    [BASIC, "Front", { kind: "basic", front: "typed", back: "Back" }],
    [BASIC, "Back", { kind: "basic", front: "Front", back: "typed" }],
    [CLOZE, "Sentence", { kind: "cloze", text: "typed", hiddenParts: ["big"] }],
    [
      CLOZE,
      "Hidden parts, one per line",
      { kind: "cloze", text: "a big secret", hiddenParts: ["typed"] },
    ],
    [
      LIST,
      "Question",
      { kind: "list", question: "typed", items: ["one", "two"] },
    ],
    [
      LIST,
      "Items, one per line",
      { kind: "list", question: "Name them", items: ["typed"] },
    ],
    [
      FEYNMAN,
      "Explain this",
      {
        kind: "feynman",
        prompt: "typed",
        referenceExplanation: "Mass bends spacetime",
      },
    ],
    [
      FEYNMAN,
      "Reference explanation",
      {
        kind: "feynman",
        prompt: "Explain gravity",
        referenceExplanation: "typed",
      },
    ],
  ] as const)("reports an edit to %s's %s", (face, label, expected) => {
    const onChange = vi.fn();
    render(() => <FlashcardFields face={face} onChange={onChange} />);

    fireEvent.input(screen.getByLabelText(label), {
      target: { value: "typed" },
    });

    expect(onChange).toHaveBeenCalledWith(expected);
  });
});

describe("FlashcardRatings", () => {
  it("reports the rating whose button was pressed", () => {
    fc.assert(
      fc.property(fc.constantFrom(1, 2, 3, 4 as const), (rating) => {
        const onRate = vi.fn();
        const labels = { 1: "Again", 2: "Hard", 3: "Good", 4: "Easy" };
        const { unmount } = render(() => (
          <FlashcardRatings intervals={null} onRate={onRate} />
        ));

        fireEvent.click(
          screen.getByRole("button", { name: new RegExp(labels[rating]) }),
        );

        expect(onRate).toHaveBeenCalledWith(rating);
        unmount();
      }),
      { numRuns: 4 },
    );
  });

  it("shows no interval before the schedule is known", () => {
    render(() => <FlashcardRatings intervals={null} onRate={vi.fn()} />);

    expect(
      [...document.querySelectorAll(".rating-interval")].map(
        (s) => s.textContent,
      ),
    ).toEqual(["", "", "", ""]);
  });

  it("shows the next interval for every rating", () => {
    render(() => (
      <FlashcardRatings
        intervals={{ 1: 60, 2: 3600, 3: 86400, 4: 2592000 }}
        onRate={vi.fn()}
      />
    ));

    expect(
      [...document.querySelectorAll(".rating-interval")].map(
        (s) => s.textContent,
      ),
    ).toEqual(["1 min", "1 h", "1 days", "1 mo"]);
  });
});

describe("ConfirmDialog", () => {
  it("confirms when the confirm button is pressed", () => {
    const onConfirm = vi.fn();
    render(() => (
      <ConfirmDialog
        title="Delete this card?"
        description="It leaves the deck for good."
        confirmLabel="Delete card"
        onConfirm={onConfirm}
        onCancel={vi.fn()}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Delete card" }));

    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it("cancels when the backdrop is clicked", () => {
    const onCancel = vi.fn();
    render(() => (
      <ConfirmDialog
        title="t"
        description="d"
        confirmLabel="Delete"
        onConfirm={vi.fn()}
        onCancel={onCancel}
      />
    ));

    fireEvent.click(document.querySelector<HTMLElement>(".modal-backdrop")!);

    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("cancels from either the footer or the head", () => {
    const onCancel = vi.fn();
    render(() => (
      <ConfirmDialog
        title="t"
        description="d"
        confirmLabel="Delete"
        onConfirm={vi.fn()}
        onCancel={onCancel}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    fireEvent.click(screen.getByRole("button", { name: "Close dialog" }));

    expect(onCancel).toHaveBeenCalledTimes(2);
  });
});
