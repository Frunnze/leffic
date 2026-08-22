import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import {
  GenerationChoice,
} from "../src/features/folder/import/GenerationChoice";
import {
  GenerationChoices,
} from "../src/features/folder/import/GenerationChoices";
import {
  FLASHCARD_TYPES,
  ImportOptions,
} from "../src/features/folder/import/import-options";
import "./import-views-support";

describe("GenerationChoice", () => {
  function renderChoice(
    choice = ImportOptions.emptyChoice(),
    onChange = vi.fn(),
  ): void {
    render(() => (
      <GenerationChoice
        name="flashcards"
        label="Flashcards"
        hint="Recall one fact at a time"
        types={FLASHCARD_TYPES}
        choice={choice}
        onChange={onChange}
      />
    ));
  }

  it("hides the types until the kind is chosen", () => {
    renderChoice();

    expect(document.querySelector(".choice-options")).toBeNull();
  });

  it("chooses the kind", () => {
    const onChange = vi.fn();
    renderChoice(ImportOptions.emptyChoice(), onChange);

    fireEvent.click(screen.getByLabelText(/Flashcards/));

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ isChosen: true }),
    );
  });

  it("shows every type once the kind is chosen", () => {
    renderChoice({ isChosen: true, counts: {}, chosenTypes: [] });

    expect(screen.getByLabelText("Basic")).toBeTruthy();
    expect(screen.queryByLabelText("flashcards-basic")).toBeNull();
  });

  it("chooses a type", () => {
    const onChange = vi.fn();
    renderChoice({ isChosen: true, counts: {}, chosenTypes: [] }, onChange);

    fireEvent.change(screen.getByLabelText("Basic"));

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ chosenTypes: ["basic"] }),
    );
  });

  it("counts a chosen type", () => {
    const onChange = vi.fn();
    renderChoice(
      { isChosen: true, counts: {}, chosenTypes: ["basic"] },
      onChange,
    );

    fireEvent.change(screen.getByLabelText("20"));

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ counts: { basic: 20 } }),
    );
  });

  it("drops the custom count once a preset is chosen", () => {
    const onChange = vi.fn();
    renderChoice(
      { isChosen: true, counts: {}, chosenTypes: ["basic"] },
      onChange,
    );

    fireEvent.change(screen.getByLabelText("Custom"));
    fireEvent.change(screen.getByLabelText("10"));

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ counts: { basic: 10 } }),
    );
    expect(screen.queryByLabelText("How many for flashcards-basic")).toBeNull();
  });

  it("keeps a cleared custom count custom", () => {
    const onChange = vi.fn();
    renderChoice(
      { isChosen: true, counts: {}, chosenTypes: ["basic"] },
      onChange,
    );

    fireEvent.change(screen.getByLabelText("Custom"));
    fireEvent.change(screen.getByLabelText("Auto"));

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ counts: { basic: null } }),
    );
  });
});

describe("GenerationChoices", () => {
  function renderChoices(isNoteAlreadyMade: boolean): void {
    render(() => (
      <GenerationChoices
        isNoteAlreadyMade={isNoteAlreadyMade}
        flashcards={ImportOptions.emptyChoice()}
        test={ImportOptions.emptyChoice()}
        note={ImportOptions.emptyChoice()}
        onFlashcardsChange={vi.fn()}
        onTestChange={vi.fn()}
        onNoteChange={vi.fn()}
      />
    ));
  }

  it("offers a note only when one was not written already", () => {
    fc.assert(
      fc.property(fc.boolean(), (isNoteAlreadyMade) => {
        const { unmount } = render(() => (
          <GenerationChoices
            isNoteAlreadyMade={isNoteAlreadyMade}
            flashcards={ImportOptions.emptyChoice()}
            test={ImportOptions.emptyChoice()}
            note={ImportOptions.emptyChoice()}
            onFlashcardsChange={vi.fn()}
            onTestChange={vi.fn()}
            onNoteChange={vi.fn()}
          />
        ));

        expect(document.querySelectorAll(".units-choice")).toHaveLength(
          isNoteAlreadyMade ? 2 : 3,
        );
        unmount();
      }),
      { numRuns: 2 },
    );
  });

  it("offers flashcards and a test", () => {
    renderChoices(true);

    expect(screen.getByLabelText(/Flashcards/)).toBeTruthy();
    expect(screen.getByLabelText(/^Test/)).toBeTruthy();
  });

  it.each([
    [/Flashcards/, "onFlashcardsChange"],
    [/^Test/, "onTestChange"],
    [/^Note/, "onNoteChange"],
  ] as const)("reports a change to %s", (label, handlerName) => {
    const handlers = {
      onFlashcardsChange: vi.fn(),
      onTestChange: vi.fn(),
      onNoteChange: vi.fn(),
    };
    render(() => (
      <GenerationChoices
        isNoteAlreadyMade={false}
        flashcards={ImportOptions.emptyChoice()}
        test={ImportOptions.emptyChoice()}
        note={ImportOptions.emptyChoice()}
        {...handlers}
      />
    ));

    fireEvent.click(screen.getByLabelText(label));

    expect(handlers[handlerName]).toHaveBeenCalledWith(
      expect.objectContaining({ isChosen: true }),
    );
  });
});
