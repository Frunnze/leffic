import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@solidjs/testing-library";
import { GenerationApi } from "../src/features/folder/import/generation-api";
import {
  GenerationWatcher,
} from "../src/features/folder/import/generation-watcher";
import { ImportFlow } from "../src/features/folder/import/ImportFlow";
import { NotesApi } from "../src/shared/notes/notes-api";
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
        <ImportFlow
          folderId="home"
          folderName="Biology"
          isOpen={isOpen}
          onClose={onClose}
          onUnitsAdded={onUnitsAdded}
        />
        <FlowToasts />
      </ToastProvider>
    ));
  }

  it("writes a note from a topic and reviews it", async () => {
    const made = unitOf({ id: "note-1", name: "Mitosis", type: "note" });
    vi.spyOn(GenerationApi, "start").mockResolvedValue({
      ...NO_TASKS,
      noteTaskId: "n1",
    });
    vi.spyOn(GenerationWatcher, "awaitOne").mockResolvedValue({
      kind: "note",
      succeeded: true,
      units: [made],
    });
    vi.spyOn(NotesApi, "note").mockResolvedValue({
      name: "Mitosis",
      content: "<p>cells divide</p>",
      readingMinutes: 1,
      isRead: false,
    });
    const onUnitsAdded = vi.fn();
    renderFlow(onUnitsAdded);

    fireEvent.change(screen.getByLabelText("Topic"));
    fireEvent.input(document.querySelector("#import-topic") as HTMLElement, {
      target: { value: "mitosis" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() =>
      expect(screen.getByLabelText("Note")).toHaveProperty(
        "value",
        "cells divide",
      ),
    );
    expect(onUnitsAdded).toHaveBeenCalledWith([made], "home");
  });

  it("announces a note that could not be written", async () => {
    vi.spyOn(GenerationApi, "start").mockResolvedValue(NO_TASKS);
    vi.spyOn(GenerationWatcher, "awaitOne").mockResolvedValue({
      kind: "note",
      succeeded: false,
      units: [],
    });
    renderFlow();

    fireEvent.change(screen.getByLabelText("Topic"));
    fireEvent.input(document.querySelector("#import-topic") as HTMLElement, {
      target: { value: "mitosis" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() =>
      expect(toastTitles()).toContain("Couldn't write the note"),
    );
  });

  it("extracts the text of an uploaded file", async () => {
    vi.spyOn(GenerationApi, "uploadFile").mockResolvedValue([
      { fileId: "9", name: "notes.pdf", extension: "pdf", createdAt: "now" },
    ]);
    const extracting = vi
      .spyOn(GenerationApi, "extractText")
      .mockResolvedValue("the file text");
    renderFlow();

    const input = document.querySelector("#import-file") as HTMLInputElement;
    Object.defineProperty(input, "files", {
      value: [pdfFile()],
      writable: true,
    });
    fireEvent.change(input);
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() =>
      expect(screen.getByLabelText("Text")).toHaveProperty(
        "value",
        "the file text",
      ),
    );
    expect(extracting).toHaveBeenCalledTimes(1);
  });

  it("reviews nothing when the upload stored nothing", async () => {
    vi.spyOn(GenerationApi, "uploadFile").mockResolvedValue([]);
    renderFlow();

    const input = document.querySelector("#import-file") as HTMLInputElement;
    Object.defineProperty(input, "files", {
      value: [pdfFile()],
      writable: true,
    });
    fireEvent.change(input);
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() =>
      expect(screen.getByLabelText("Text")).toHaveProperty("value", ""),
    );
  });
});
