import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { FlashcardsApi } from "../src/features/flashcards/flashcards-api";
import {
  CARD,
  INTERVALS,
  SECOND_CARD,
  TOMORROW,
  deckOf,
  renderReview,
} from "./flashcards-review-support";

describe("FlashcardsReview", () => {
  it("saves an edited card in place", async () => {
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(deckOf(CARD));
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    const updating = vi
      .spyOn(FlashcardsApi, "update")
      .mockResolvedValue(undefined);
    renderReview();

    await waitFor(() =>
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Edit card" }));
    fireEvent.input(screen.getByLabelText("Front"), {
      target: { value: "edited" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() => expect(updating).toHaveBeenCalledTimes(1));
    expect(document.querySelector(".flashcard-prompt")?.textContent).toBe(
      "edited",
    );
  });

  it("removes a deleted card from the queue", async () => {
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(
      deckOf(CARD, SECOND_CARD),
    );
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    const removing = vi
      .spyOn(FlashcardsApi, "remove")
      .mockResolvedValue(undefined);
    renderReview();

    await waitFor(() =>
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Delete card" }));
    fireEvent.click(screen.getByRole("button", { name: "Delete card" }));

    await waitFor(() => expect(removing).toHaveBeenCalledWith("1"));
    expect(document.querySelector(".flashcard-prompt")?.textContent).toBe(
      "second",
    );
  });

  it("reloads the deck when the last card is deleted", async () => {
    const loading = vi
      .spyOn(FlashcardsApi, "deck")
      .mockResolvedValueOnce(deckOf(CARD))
      .mockResolvedValueOnce(null);
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    vi.spyOn(FlashcardsApi, "remove").mockResolvedValue(undefined);
    renderReview();

    await waitFor(() =>
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this card" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Delete card" }));
    fireEvent.click(screen.getByRole("button", { name: "Delete card" }));

    await waitFor(() => expect(loading).toHaveBeenCalledTimes(2));
  });

  it("asks the chatbot for a mnemonic about the card", async () => {
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(deckOf(CARD));
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    renderReview();

    await waitFor(() =>
      screen.getByRole("button", {
        name: "Ask for a way to memorise this card",
      }),
    );
    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask for a way to memorise this card",
      }),
    );

    expect(document.querySelector(".flashcard")).toBeTruthy();
  });

  it("rates the card from the keyboard", async () => {
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(
      deckOf(CARD, SECOND_CARD),
    );
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    const reviewing = vi.spyOn(FlashcardsApi, "review").mockResolvedValue({
      dueDate: TOMORROW,
      newFsrsCard: {},
    });
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.keyDown(document, { key: " " });
    fireEvent.keyDown(document, { key: "3" });

    await waitFor(() => expect(reviewing).toHaveBeenCalledWith("1", 3));
  });
});
