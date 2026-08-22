import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import { ImportDialog } from "../src/features/folder/import/ImportDialog";
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

  it("takes a link as the source", () => {
    const onExtract = vi
      .fn()
      .mockResolvedValue({ text: "page text", isNoteAlreadyMade: false });
    renderDialog(onExtract);

    fireEvent.change(screen.getByLabelText("Link"));
    fireEvent.input(document.querySelector("#import-link") as HTMLElement, {
      target: { value: "https://example.test" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    expect(onExtract).toHaveBeenCalledWith(
      expect.objectContaining({ link: "https://example.test" }),
    );
  });

  it("changes what it will generate", () => {
    const onGenerate = vi.fn();
    renderDialog(undefined, onGenerate);

    fireEvent.change(screen.getByLabelText("Text"));
    fireEvent.input(document.querySelector("#import-text") as HTMLElement, {
      target: { value: "pasted" },
    });
    fireEvent.click(screen.getByLabelText(/^Test/));
    fireEvent.click(screen.getByRole("button", { name: "Generate" }));

    expect(onGenerate).toHaveBeenCalledWith(
      expect.objectContaining({
        test: expect.objectContaining({ isChosen: false }),
      }),
      "pasted",
    );
  });

  it("cancels from the footer, the head and the backdrop", () => {
    const onCancel = vi.fn();
    renderDialog(undefined, vi.fn(), vi.fn(), onCancel);

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    fireEvent.click(screen.getByRole("button", { name: "Close dialog" }));
    fireEvent.click(document.querySelector(".modal-backdrop") as HTMLElement);

    expect(onCancel).toHaveBeenCalledTimes(3);
  });
});
