import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@solidjs/testing-library";
import { ImportDialog } from "../src/features/folder/import/ImportDialog";
import { pdfFile } from "./import-factories";
import "./import-flow-support";

describe("ImportDialog", () => {
  function renderDialog(
    onExtract = vi
      .fn()
      .mockResolvedValue({ text: "read", isNoteAlreadyMade: false }),
    onGenerate = vi.fn(),
    onUploadOnly = vi.fn(),
    onCancel = vi.fn(),
  ): void {
    render(() => (
      <ImportDialog
        folderName="Biology"
        onExtract={onExtract}
        onGenerate={onGenerate}
        onUploadOnly={onUploadOnly}
        onCancel={onCancel}
      />
    ));
  }

  it("names the folder it will save into", () => {
    renderDialog();

    expect(document.querySelector(".modal-text")?.textContent).toBe(
      "Saved into Biology.",
    );
  });

  it("asks for a file before it can continue", () => {
    renderDialog();

    expect(document.querySelector(".modal-foot-hint")?.textContent).toBe(
      "Choose a file first.",
    );
  });

  it("shows the generation choices straight away for pasted text", () => {
    renderDialog();

    fireEvent.change(screen.getByLabelText("Text"));

    expect(screen.getByLabelText(/Flashcards/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Generate" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("reads the source, then shows the review and the choices", async () => {
    const onExtract = vi
      .fn()
      .mockResolvedValue({ text: "the text", isNoteAlreadyMade: false });
    renderDialog(onExtract);

    fireEvent.change(screen.getByLabelText("Topic"));
    fireEvent.input(document.querySelector("#import-topic") as HTMLElement, {
      target: { value: "mitosis" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() =>
      expect(screen.getByLabelText("Text")).toHaveProperty("value", "the text"),
    );
    expect(onExtract).toHaveBeenCalledTimes(1);
  });

  it("says it is writing a note while a topic is read", async () => {
    const onExtract = vi
      .fn()
      .mockImplementation(() => new Promise(() => undefined));
    renderDialog(onExtract);

    fireEvent.change(screen.getByLabelText("Topic"));
    fireEvent.input(document.querySelector("#import-topic") as HTMLElement, {
      target: { value: "mitosis" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() =>
      expect(document.querySelector(".modal-wait-text")?.textContent).toContain(
        "Writing a note about mitosis",
      ),
    );
  });

  it("drops the note choice once a note was already written", async () => {
    const onExtract = vi
      .fn()
      .mockResolvedValue({ text: "note text", isNoteAlreadyMade: true });
    renderDialog(onExtract);

    fireEvent.change(screen.getByLabelText("Topic"));
    fireEvent.input(document.querySelector("#import-topic") as HTMLElement, {
      target: { value: "mitosis" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() => expect(screen.getByLabelText("Note")).toBeTruthy());
    expect(document.querySelectorAll(".units-choice")).toHaveLength(2);
  });

  it("generates from the reviewed text", async () => {
    const onGenerate = vi.fn();
    renderDialog(undefined, onGenerate);

    fireEvent.change(screen.getByLabelText("Topic"));
    fireEvent.input(document.querySelector("#import-topic") as HTMLElement, {
      target: { value: "mitosis" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));
    await waitFor(() => screen.getByRole("button", { name: "Generate" }));
    fireEvent.input(screen.getByLabelText("Text"), {
      target: { value: "trimmed" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate" }));

    expect(onGenerate).toHaveBeenCalledWith(
      expect.objectContaining({ kind: "topic", topic: "mitosis" }),
      "trimmed",
    );
  });

  it("generates straight from pasted text", () => {
    const onGenerate = vi.fn();
    renderDialog(undefined, onGenerate);

    fireEvent.change(screen.getByLabelText("Text"));
    fireEvent.input(document.querySelector("#import-text") as HTMLElement, {
      target: { value: "pasted" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate" }));

    expect(onGenerate).toHaveBeenCalledWith(
      expect.objectContaining({ kind: "text" }),
      "pasted",
    );
  });

  it("uploads a file without generating anything", () => {
    const onUploadOnly = vi.fn();
    const chosen = pdfFile();
    renderDialog(undefined, vi.fn(), onUploadOnly);

    const input = document.querySelector("#import-file") as HTMLInputElement;
    Object.defineProperty(input, "files", { value: [chosen], writable: true });
    fireEvent.change(input);
    fireEvent.click(screen.getByRole("button", { name: "Upload only" }));

    expect(onUploadOnly).toHaveBeenCalledWith(chosen);
  });

  it("carries the chosen page range into what it extracts", () => {
    const onExtract = vi
      .fn()
      .mockResolvedValue({ text: "read", isNoteAlreadyMade: false });
    renderDialog(onExtract);

    const input = document.querySelector("#import-file") as HTMLInputElement;
    Object.defineProperty(input, "files", {
      value: [pdfFile()],
      writable: true,
    });
    fireEvent.change(input);
    fireEvent.input(screen.getByLabelText("First page"), {
      target: { value: "2" },
    });
    fireEvent.input(screen.getByLabelText("Last page"), {
      target: { value: "6" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    expect(onExtract).toHaveBeenCalledWith(
      expect.objectContaining({ firstPage: 2, lastPage: 6 }),
    );
  });
});
