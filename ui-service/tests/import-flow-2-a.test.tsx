import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@solidjs/testing-library";
import fc from "fast-check";
import { GenerationApi } from "../src/features/folder/import/generation-api";
import { GenerationProvider } from "../src/features/folder/import/GenerationContext";
import {
  GenerationWatcher,
} from "../src/features/folder/import/generation-watcher";
import { ImportFlow } from "../src/features/folder/import/ImportFlow";
import { ToastProvider } from "../src/shared/notifications/ToastContext";
import { pdfFile } from "./import-factories";
import { unitOf } from "./unit-factories";
import { FlowToasts, NO_TASKS, toastTitles } from "./import-flow-support";

describe("ImportFlow", () => {
  function renderFlow(
    onUnitsAdded = vi.fn(),
    onClose = vi.fn(),
    isOpen = true,
  ): void {
    render(() => (
      <ToastProvider>
        <GenerationProvider>
          <ImportFlow
            folderId="home"
            folderName="Biology"
            isOpen={isOpen}
            onClose={onClose}
            onUnitsAdded={onUnitsAdded}
          />
          <FlowToasts />
        </GenerationProvider>
      </ToastProvider>
    ));
  }

  function pasteText(value: string): void {
    fireEvent.change(screen.getByLabelText("Text"));
    fireEvent.input(document.querySelector("#import-text") as HTMLElement, {
      target: { value },
    });
  }

  beforeEach(() => {
    vi.spyOn(GenerationWatcher, "watch").mockReturnValue(() => undefined);
  });

  it("opens the dialog only when it is asked to", () => {
    fc.assert(
      fc.property(fc.boolean(), (isOpen) => {
        const { unmount } = render(() => (
          <ToastProvider>
            <GenerationProvider>
              <ImportFlow
                folderId="home"
                folderName="Biology"
                isOpen={isOpen}
                onClose={vi.fn()}
                onUnitsAdded={vi.fn()}
              />
            </GenerationProvider>
          </ToastProvider>
        ));

        expect(document.querySelector(".modal") !== null).toBe(isOpen);
        unmount();
      }),
      { numRuns: 2 },
    );
  });

  it("closes when the dialog is cancelled", () => {
    const onClose = vi.fn();
    renderFlow(vi.fn(), onClose);

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("starts the generation and watches it", async () => {
    const starting = vi
      .spyOn(GenerationApi, "start")
      .mockResolvedValue(NO_TASKS);
    const onClose = vi.fn();
    renderFlow(vi.fn(), onClose);

    pasteText("pasted");
    fireEvent.click(screen.getByRole("button", { name: "Generate" }));

    await waitFor(() => expect(starting).toHaveBeenCalledTimes(1));
    expect(onClose).toHaveBeenCalledTimes(1);
    expect(toastTitles()).toContain("Generating from your text");
  });

  it("announces every finished generation above the flow", async () => {
    vi.spyOn(GenerationApi, "start").mockResolvedValue(NO_TASKS);
    const made = unitOf({ id: "made", name: "Deck", type: "flashcard_deck" });
    vi.spyOn(GenerationWatcher, "watch").mockImplementation((_, onOutcome) => {
      onOutcome({ kind: "flashcards", succeeded: true, units: [made] });

      return () => undefined;
    });
    renderFlow();

    pasteText("pasted");
    fireEvent.click(screen.getByRole("button", { name: "Generate" }));

    await waitFor(() => expect(toastTitles()).toContain("Flashcards ready"));
  });

  it("announces a generation that failed", async () => {
    vi.spyOn(GenerationApi, "start").mockResolvedValue(NO_TASKS);
    vi.spyOn(GenerationWatcher, "watch").mockImplementation((_, onOutcome) => {
      onOutcome({ kind: "test", succeeded: false, units: [] });

      return () => undefined;
    });
    renderFlow();

    pasteText("pasted");
    fireEvent.click(screen.getByRole("button", { name: "Generate" }));

    await waitFor(() =>
      expect(toastTitles()).toContain("Couldn't generate the test"),
    );
  });

  it("uploads a file on its own", async () => {
    const uploaded = {
      fileId: "9",
      name: "notes.pdf",
      extension: "pdf",
      createdAt: "now",
    };
    vi.spyOn(GenerationApi, "uploadFile").mockResolvedValue([uploaded]);
    const onUnitsAdded = vi.fn();
    renderFlow(onUnitsAdded);

    const input = document.querySelector("#import-file") as HTMLInputElement;
    Object.defineProperty(input, "files", {
      value: [pdfFile()],
      writable: true,
    });
    fireEvent.change(input);
    fireEvent.click(screen.getByRole("button", { name: "Upload only" }));

    await waitFor(() => expect(toastTitles()).toContain("notes.pdf uploaded"));
    expect(onUnitsAdded).toHaveBeenCalledWith(
      [
        {
          id: "9",
          name: "notes.pdf",
          type: "file",
          createdAt: "now",
          extension: "pdf",
          dueCount: null,
          meta: null,
        },
      ],
      "home",
    );
  });

  it("announces an upload that failed", async () => {
    vi.spyOn(GenerationApi, "uploadFile").mockRejectedValue(new Error("no"));
    renderFlow();

    const input = document.querySelector("#import-file") as HTMLInputElement;
    Object.defineProperty(input, "files", {
      value: [pdfFile()],
      writable: true,
    });
    fireEvent.change(input);
    fireEvent.click(screen.getByRole("button", { name: "Upload only" }));

    await waitFor(() =>
      expect(toastTitles()).toContain("Couldn't upload notes.pdf"),
    );
  });
});
