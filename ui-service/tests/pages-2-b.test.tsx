import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import FolderPage from "../src/features/folder/FolderPage";
import { GenerationProvider } from "../src/features/folder/import/GenerationContext";
import { GenerationApi } from "../src/features/folder/import/generation-api";
import {
  GenerationWatcher,
} from "../src/features/folder/import/generation-watcher";
import { StatsApi } from "../src/features/folder/stats-api";
import type {
  GenerationOutcome,
} from "../src/features/folder/import/generation-tally";
import { ToastProvider } from "../src/shared/notifications/ToastContext";
import { UnitsApi } from "../src/features/folder/units-api";
import { unitOf } from "./unit-factories";
import { renderAt } from "./router-support";
import { NOTHING_DUE, stubAccount } from "./pages-support";

describe("FolderPage", () => {
  function renderFolder(breakdown = NOTHING_DUE): ReturnType<typeof renderAt> {
    stubAccount();
    vi.spyOn(StatsApi, "dueBreakdown").mockResolvedValue(breakdown);

    return renderAt("/folder/home", "/folder/:id", () => (
      <ToastProvider>
        <GenerationProvider>
          <AskProvider>
            <FolderPage />
          </AskProvider>
        </GenerationProvider>
      </ToastProvider>
    ));
  }

  it("keeps a unit that was generated for the folder left behind", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [unitOf({ id: "1", name: "Cells", type: "note" })],
    });
    vi.spyOn(GenerationApi, "start").mockResolvedValue({
      flashcardsTaskIds: [],
      noteTaskId: null,
      testTaskIds: [],
    });
    const reports: ((outcome: GenerationOutcome) => void)[] = [];
    vi.spyOn(GenerationWatcher, "watch").mockImplementation((_, onOutcome) => {
      reports.push(onOutcome);

      return () => undefined;
    });
    const { history } = renderFolder();

    await waitFor(() => screen.getByRole("button", { name: "Import" }));
    fireEvent.click(screen.getByRole("button", { name: "Import" }));
    fireEvent.change(screen.getByLabelText("Text"));
    fireEvent.input(document.querySelector("#import-text") as HTMLElement, {
      target: { value: "pasted" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate" }));

    await waitFor(() => expect(reports).toHaveLength(1));
    history.set({ value: "/folder/other" });
    await waitFor(() => expect(history.get()).toBe("/folder/other"));

    reports[0]?.({
      kind: "note",
      succeeded: true,
      units: [unitOf({ id: "made", name: "Made elsewhere", type: "note" })],
    });

    expect(document.body.textContent).not.toContain("Made elsewhere");
  });

  it("renames a unit in place", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [
        unitOf({ id: "1", name: "Cells", type: "note" }),
        unitOf({ id: "2", name: "Mitosis notes", type: "note" }),
      ],
    });
    const renaming = vi.spyOn(UnitsApi, "rename").mockResolvedValue(undefined);
    renderFolder();

    await waitFor(() =>
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Rename" }));
    fireEvent.input(screen.getByLabelText("Name"), {
      target: { value: "Mitosis" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(document.querySelector(".unit-name")?.textContent).toBe("Mitosis"),
    );
    expect(renaming).toHaveBeenCalledWith("1", "note", "Mitosis");
  });

  it("moves a unit out of the folder", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [unitOf({ id: "1", name: "Cells", type: "note" })],
    });
    const moving = vi.spyOn(UnitsApi, "move").mockResolvedValue(undefined);
    renderFolder();

    await waitFor(() =>
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Move to folder" }));
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(moving).toHaveBeenCalledWith("1", "note", "home"),
    );
    expect(document.querySelector(".unit-name")).toBeNull();
  });

  it("deletes a unit from the folder", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [unitOf({ id: "1", name: "Cells", type: "note" })],
    });
    const removing = vi.spyOn(UnitsApi, "remove").mockResolvedValue(undefined);
    renderFolder();

    await waitFor(() =>
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Delete" }));

    await waitFor(() => expect(removing).toHaveBeenCalledWith("1", "note"));
    expect(document.querySelector(".unit-name")).toBeNull();
  });

  it("starts a review from the due section", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [],
    });
    const { history } = renderFolder({
      ...NOTHING_DUE,
      flashcardsDue: 2,
      testItemsDue: 1,
      totalToday: 3,
    });

    await waitFor(() =>
      screen.getByRole("button", { name: /^Review 3 items/ }),
    );
    fireEvent.click(screen.getByRole("button", { name: /^Review 3 items/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: /^Flashcards/ }));

    await waitFor(() => expect(history.get()).toBe("/folder/home/flashcards"));
  });

  it("starts a test from the due section", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [],
    });
    const { history } = renderFolder({
      ...NOTHING_DUE,
      testItemsDue: 1,
      totalToday: 1,
    });

    await waitFor(() =>
      screen.getByRole("button", { name: /^Review 1 items/ }),
    );
    fireEvent.click(screen.getByRole("button", { name: /^Review 1 items/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: /^Test/ }));

    await waitFor(() => expect(history.get()).toBe("/folder/home/test"));
  });
});
