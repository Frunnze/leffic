import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { AccountApi } from "../src/features/settings/account-api";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import { FlashcardsApi } from "../src/features/flashcards/flashcards-api";
import FlashcardsPage from "../src/features/flashcards/FlashcardsPage";
import { renderAt } from "./router-support";
import "./flashcards-review-support";

describe("FlashcardsPage", () => {
  it("frames the review inside the app shell", async () => {
    vi.spyOn(AccountApi, "read").mockResolvedValue({
      username: "learner",
      email: "learner@example.test",
      theme: "system",
    });
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(null);
    renderAt("/flashcard_deck/1", "/flashcard_deck/:id", () => (
      <AskProvider>
        <FlashcardsPage scope="flashcard_deck" />
      </AskProvider>
    ));

    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Close Flashcards" }),
      ).toBeTruthy(),
    );

    fireEvent.click(screen.getByRole("button", { name: "Close Flashcards" }));

    expect(document.querySelector(".review-page")).toBeTruthy();
  });
});
