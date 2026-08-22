import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import { FlashcardActions } from "../src/features/flashcards/FlashcardActions";
import { FlashcardEditor } from "../src/features/flashcards/FlashcardEditor";
import { CARD } from "./flashcards-review-support";

describe("FlashcardEditor", () => {
  it("saves the edited face", () => {
    const onSave = vi.fn();
    render(() => (
      <FlashcardEditor card={CARD} onSave={onSave} onCancel={vi.fn()} />
    ));

    fireEvent.input(screen.getByLabelText("Front"), {
      target: { value: "new front" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).toHaveBeenCalledWith({
      kind: "basic",
      front: "new front",
      back: "a",
    });
  });

  it("refuses to save an empty side", () => {
    const onSave = vi.fn();
    render(() => (
      <FlashcardEditor card={CARD} onSave={onSave} onCancel={vi.fn()} />
    ));

    fireEvent.input(screen.getByLabelText("Back"), { target: { value: "  " } });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Save card" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("cancels from the footer, the head and the backdrop", () => {
    const onCancel = vi.fn();
    render(() => (
      <FlashcardEditor card={CARD} onSave={vi.fn()} onCancel={onCancel} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    fireEvent.click(screen.getByRole("button", { name: "Close dialog" }));
    fireEvent.click(document.querySelector(".modal-backdrop") as HTMLElement);

    expect(onCancel).toHaveBeenCalledTimes(3);
  });
});

describe("FlashcardActions", () => {
  function renderActions(
    onSave = vi.fn(),
    onDelete = vi.fn(),
    onMnemonic = vi.fn(),
  ): void {
    render(() => (
      <FlashcardActions
        card={CARD}
        onSave={onSave}
        onDelete={onDelete}
        onMnemonic={onMnemonic}
      />
    ));
  }

  it("asks for a mnemonic", () => {
    const onMnemonic = vi.fn();
    renderActions(vi.fn(), vi.fn(), onMnemonic);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask for a way to memorise this card",
      }),
    );

    expect(onMnemonic).toHaveBeenCalledTimes(1);
  });

  it("edits the card through its own menu", () => {
    const onSave = vi.fn();
    renderActions(onSave);

    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Edit card" }));
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).toHaveBeenCalledTimes(1);
    expect(document.querySelector(".modal")).toBeNull();
  });

  it("closes the editor when it is cancelled", () => {
    renderActions();

    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Edit card" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(document.querySelector(".modal")).toBeNull();
  });

  it("deletes the card once the deletion is confirmed", () => {
    const onDelete = vi.fn();
    renderActions(vi.fn(), onDelete);

    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Delete card" }));
    fireEvent.click(screen.getByRole("button", { name: "Delete card" }));

    expect(onDelete).toHaveBeenCalledTimes(1);
    expect(document.querySelector(".modal")).toBeNull();
  });

  it("keeps the card when the deletion is cancelled", () => {
    const onDelete = vi.fn();
    renderActions(vi.fn(), onDelete);

    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Delete card" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onDelete).not.toHaveBeenCalled();
    expect(document.querySelector(".modal")).toBeNull();
  });
});
