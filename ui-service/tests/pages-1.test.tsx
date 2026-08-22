import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import LandingPage from "../src/features/landing/LandingPage";
import NotePage from "../src/features/notes/NotePage";
import { NotesApi } from "../src/shared/notes/notes-api";
import { ToastProvider } from "../src/shared/notifications/ToastContext";
import { renderAt } from "./router-support";
import { NOTE, stubAccount } from "./pages-support";

describe("LandingPage", () => {
  it("invites the reader to start", () => {
    renderAt("/", "/", () => <LandingPage />);

    expect(
      screen.getByRole("link", { name: "Start free" }).getAttribute("href"),
    ).toBe("/sign-up");
    expect(screen.getByRole("link", { name: "Log in" })).toBeTruthy();
  });

  it("lists what one import produces", () => {
    renderAt("/", "/", () => <LandingPage />);

    expect(document.body.textContent).toContain("30 flashcards");
    expect(document.body.textContent).toContain("Active recall");
  });
});

describe("NotePage", () => {
  function renderNote(): void {
    stubAccount();
    renderAt("/note/3", "/note/:id", () => (
      <ToastProvider>
        <AskProvider>
          <NotePage />
        </AskProvider>
      </ToastProvider>
    ));
  }

  it("waits while the note loads", () => {
    vi.spyOn(NotesApi, "note").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderNote();

    expect(document.querySelector(".note-meta")?.textContent).toBe(
      "Loading the note…",
    );
  });

  it("shows the note and how long it takes to read", async () => {
    vi.spyOn(NotesApi, "note").mockResolvedValue(NOTE);
    renderNote();

    await waitFor(() =>
      expect(document.querySelector(".note-title")?.textContent).toBe(
        "Mitosis",
      ),
    );
    expect(document.querySelector(".note-meta")?.textContent).toBe(
      "2 min read",
    );
    expect(document.querySelector(".note-body")?.textContent).toBe(
      "cells divide",
    );
  });

  it("calls a note with no words a generated note", async () => {
    vi.spyOn(NotesApi, "note").mockResolvedValue({
      ...NOTE,
      readingMinutes: null,
    });
    renderNote();

    await waitFor(() =>
      expect(document.querySelector(".note-meta")?.textContent).toBe(
        "Generated note",
      ),
    );
  });

  it("marks the note as read", async () => {
    vi.spyOn(NotesApi, "note").mockResolvedValue(NOTE);
    const marking = vi
      .spyOn(NotesApi, "markAsRead")
      .mockResolvedValue(undefined);
    renderNote();

    await waitFor(() => screen.getByRole("button", { name: "Mark as read" }));
    fireEvent.click(screen.getByRole("button", { name: "Mark as read" }));

    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Marked as read" }),
      ).toBeTruthy(),
    );
    expect(marking).toHaveBeenCalledWith("3");
  });

  it("shows a note that was already read as read", async () => {
    vi.spyOn(NotesApi, "note").mockResolvedValue({ ...NOTE, isRead: true });
    renderNote();

    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Marked as read" }),
      ).toHaveProperty("disabled", true),
    );
  });

  it("says it is working while the note is being marked", async () => {
    vi.spyOn(NotesApi, "note").mockResolvedValue(NOTE);
    vi.spyOn(NotesApi, "markAsRead").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderNote();

    await waitFor(() => screen.getByRole("button", { name: "Mark as read" }));
    fireEvent.click(screen.getByRole("button", { name: "Mark as read" }));

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Marking…" })).toBeTruthy(),
    );
  });

  it("keeps the note unread when it could not be marked", async () => {
    vi.spyOn(NotesApi, "note").mockResolvedValue(NOTE);
    vi.spyOn(NotesApi, "markAsRead").mockRejectedValue(new Error("no"));
    renderNote();

    await waitFor(() => screen.getByRole("button", { name: "Mark as read" }));
    fireEvent.click(screen.getByRole("button", { name: "Mark as read" }));

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Mark as read" })).toBeTruthy(),
    );
  });
});
