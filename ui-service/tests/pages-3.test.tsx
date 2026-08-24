import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@solidjs/testing-library";
import fc from "fast-check";
import { AssessmentApi } from "../src/features/assessment/assessment-api";
import { FlashcardsApi } from "../src/features/flashcards/flashcards-api";
import { App } from "../src/App";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import { NotesApi } from "../src/shared/notes/notes-api";
import { StatsApi } from "../src/features/folder/stats-api";
import { GenerationProvider } from "../src/features/folder/import/GenerationContext";
import { ToastProvider } from "../src/shared/notifications/ToastContext";
import { UnitsApi } from "../src/features/folder/units-api";
import { NOTE, NOTHING_DUE, stubAccount } from "./pages-support";

describe("App", () => {
  function renderAppAt(path: string): ReturnType<typeof render> {
    window.history.replaceState({}, "", path);

    return render(() => (
      <ToastProvider>
        <GenerationProvider>
          <AskProvider>
            <App />
          </AskProvider>
        </GenerationProvider>
      </ToastProvider>
    ));
  }

  it("routes every page a signed-out learner can reach", () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          ["/", "landing-title"],
          ["/login", "auth-card"],
          ["/sign-up", "auth-card"],
        ),
        ([path, marker]) => {
          const rendered = renderAppAt(path);

          expect(document.querySelector(`.${marker}`)).toBeTruthy();
          rendered.unmount();
        },
      ),
    );
  });

  it.each([
    ["/flashcard_deck/1", "Close Flashcards"],
    ["/folder/home/flashcards", "Close Flashcards"],
    ["/test/1", "Close Test"],
    ["/folder/home/test", "Close Test"],
  ])("routes %s to its review page", async (path, closeLabel) => {
    stubAccount();
    vi.spyOn(FlashcardsApi, "deck").mockResolvedValue(null);
    vi.spyOn(AssessmentApi, "page").mockResolvedValue({
      testSession: "s",
      items: [],
      page: 1,
      perPage: 10,
      totalItems: 0,
    });
    const rendered = renderAppAt(path);

    await waitFor(() =>
      expect(screen.getByRole("button", { name: closeLabel })).toBeTruthy(),
    );
    rendered.unmount();
  });

  it("routes a note, a file, a folder and the settings", async () => {
    stubAccount();
    vi.spyOn(NotesApi, "note").mockResolvedValue(NOTE);
    const rendered = renderAppAt("/note/3");

    await waitFor(() =>
      expect(document.querySelector(".note-title")?.textContent).toBe(
        "Mitosis",
      ),
    );
    rendered.unmount();
  });

  it("shows the toast stack above every page", async () => {
    stubAccount();
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [],
    });
    vi.spyOn(StatsApi, "dueBreakdown").mockResolvedValue(NOTHING_DUE);
    vi.spyOn(UnitsApi, "createFolder").mockRejectedValue(new Error("no"));
    const rendered = renderAppAt("/folder/home");

    await waitFor(() => screen.getByRole("button", { name: "New folder" }));
    fireEvent.click(screen.getByRole("button", { name: "New folder" }));
    fireEvent.input(screen.getByLabelText("Folder name"), {
      target: { value: "Cells" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(document.querySelector(".toast-title")?.textContent).toBe(
        "Couldn't create the folder",
      ),
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: 'Dismiss "Couldn\'t create the folder"',
      }),
    );

    expect(document.querySelector(".toast")).toBeNull();
    rendered.unmount();
  });
});
