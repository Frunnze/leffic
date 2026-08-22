import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import fc from "fast-check";
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
  it("says it is loading before the deck arrives", () => {
    vi.spyOn(FlashcardsApi, "deck").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderReview();

    expect(document.body.textContent).toContain("Loading your cards…");
  });

  it("says the deck is done when nothing is due", async () => {
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(null);
    renderReview();

    await waitFor(() =>
      expect(document.querySelector(".state-title")?.textContent).toBe(
        "You're done for today",
      ),
    );
    expect(document.querySelector(".meter-block")).toBeNull();
  });

  it("shows the first card and its progress", async () => {
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(deckOf(CARD));
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    renderReview();

    await waitFor(() =>
      expect(document.querySelector(".flashcard-prompt")?.textContent).toBe(
        "q",
      ),
    );
    expect(document.querySelector(".meter-legend")?.textContent).toContain(
      "Reviewed 0 of 1",
    );
  });

  it("reveals the answer", async () => {
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(deckOf(CARD));
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.click(screen.getByRole("button", { name: /Show answer/ }));

    await waitFor(() =>
      expect(document.querySelector(".flashcard-answer")?.textContent).toBe(
        "a",
      ),
    );
  });

  it("reviews the card at whatever rating was pressed", async () => {
    await fc.assert(
      fc.asyncProperty(fc.constantFrom(1, 2, 3, 4 as const), async (rating) => {
        vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(
          deckOf(CARD, SECOND_CARD),
        );
        vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
        const reviewing = vi.spyOn(FlashcardsApi, "review").mockResolvedValue({
          dueDate: TOMORROW,
          newFsrsCard: {},
        });
        const rendered = renderReview();

        await waitFor(() =>
          screen.getByRole("button", { name: /Show answer/ }),
        );
        fireEvent.click(screen.getByRole("button", { name: /Show answer/ }));
        const labels = { 1: "Again", 2: "Hard", 3: "Good", 4: "Easy" };
        fireEvent.click(
          screen.getByRole("button", { name: new RegExp(labels[rating]) }),
        );

        await waitFor(() =>
          expect(reviewing).toHaveBeenCalledWith("1", rating),
        );
        rendered.unmount();
        vi.restoreAllMocks();
      }),
      { numRuns: 4 },
    );
  });

  it("counts a card scheduled for another day as reviewed", async () => {
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(
      deckOf(CARD, SECOND_CARD),
    );
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    vi.spyOn(FlashcardsApi, "review").mockResolvedValue({
      dueDate: TOMORROW,
      newFsrsCard: {},
    });
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.click(screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.click(screen.getByRole("button", { name: /Good/ }));

    await waitFor(() =>
      expect(document.querySelector(".meter-legend")?.textContent).toContain(
        "Reviewed 1 of 2",
      ),
    );
  });

  it("does not count a card that comes back today", async () => {
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(
      deckOf(CARD, SECOND_CARD),
    );
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    vi.spyOn(FlashcardsApi, "review").mockResolvedValue({
      dueDate: new Date().toISOString(),
      newFsrsCard: {},
    });
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.click(screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.click(screen.getByRole("button", { name: /Again/ }));

    await waitFor(() =>
      expect(document.querySelector(".meter-legend")?.textContent).toContain(
        "Reviewed 0 of 2",
      ),
    );
  });

  it("reloads the deck once the last card is rated", async () => {
    const loading = vi
      .spyOn(FlashcardsApi, "deck")
      .mockResolvedValueOnce(deckOf(CARD))
      .mockResolvedValueOnce(null);
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    vi.spyOn(FlashcardsApi, "review").mockResolvedValue({
      dueDate: TOMORROW,
      newFsrsCard: {},
    });
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.click(screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.click(screen.getByRole("button", { name: /Good/ }));

    await waitFor(() => expect(loading).toHaveBeenCalledTimes(2));
    await waitFor(() =>
      expect(document.querySelector(".state-title")?.textContent).toBe(
        "You're done for today",
      ),
    );
  });

  it("keeps the original total when the deck reloads", async () => {
    vi.spyOn(FlashcardsApi, "deck")
      .mockResolvedValueOnce(deckOf(CARD))
      .mockResolvedValueOnce(deckOf(SECOND_CARD));
    vi.spyOn(FlashcardsApi, "ratingIntervals").mockResolvedValue(INTERVALS);
    vi.spyOn(FlashcardsApi, "review").mockResolvedValue({
      dueDate: TOMORROW,
      newFsrsCard: {},
    });
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.click(screen.getByRole("button", { name: /Show answer/ }));
    fireEvent.click(screen.getByRole("button", { name: /Good/ }));

    await waitFor(() =>
      expect(document.querySelector(".flashcard-prompt")?.textContent).toBe(
        "second",
      ),
    );
    expect(document.querySelector(".meter-legend")?.textContent).toContain(
      "Reviewed 1 of 1",
    );
  });
});
