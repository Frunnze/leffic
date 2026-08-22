import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { ImportFooter } from "../src/features/folder/import/ImportFooter";
import {
  ImportReview,
  ImportWait,
} from "../src/features/folder/import/ImportReview";
import { pdfFile } from "./import-factories";
import "./import-views-support";

describe("ImportWait", () => {
  it("says what it is doing to the source", () => {
    fc.assert(
      fc.property(fc.boolean(), (isWritingNote) => {
        const { unmount } = render(() => (
          <ImportWait isWritingNote={isWritingNote} sourceName="notes.pdf" />
        ));

        expect(
          document.querySelector(".modal-wait-text")?.textContent,
        ).toContain(
          isWritingNote ? "Writing a note about" : "Reading notes.pdf",
        );
        unmount();
      }),
      { numRuns: 2 },
    );
  });
});

describe("ImportReview", () => {
  function renderReview(
    isNoteAlreadyMade: boolean,
    onTextChange = vi.fn(),
  ): void {
    render(() => (
      <ImportReview
        sourceName="notes.pdf"
        isNoteAlreadyMade={isNoteAlreadyMade}
        text="extracted"
        onTextChange={onTextChange}
      />
    ));
  }

  it("names the source it read", () => {
    renderReview(false);

    expect(document.querySelector(".review-source")?.textContent).toContain(
      "From notes.pdf",
    );
  });

  it("calls the extracted text Text before a note exists", () => {
    renderReview(false);

    expect(screen.getByLabelText("Text")).toHaveProperty("value", "extracted");
    expect(document.querySelector(".field-hint")?.textContent).toContain(
      "Trim anything that should not become study material.",
    );
  });

  it("calls it the Note once one was written", () => {
    renderReview(true);

    expect(screen.getByLabelText("Note")).toBeTruthy();
    expect(document.querySelector(".field-hint")?.textContent).toContain(
      "Your note is saved in the folder.",
    );
  });

  it("reports the trimmed-down text", () => {
    const onTextChange = vi.fn();
    renderReview(false, onTextChange);

    fireEvent.input(screen.getByLabelText("Text"), {
      target: { value: "shorter" },
    });

    expect(onTextChange).toHaveBeenCalledWith("shorter");
  });
});

describe("ImportFooter", () => {
  function renderFooter(
    overrides: Partial<{
      missingSource: string | null;
      nothingChosen: boolean;
      isReviewing: boolean;
      isExtracting: boolean;
      uploadableFile: File | null;
      onCancel: () => void;
      onUploadOnly: (file: File) => void;
      onContinue: () => void;
      onGenerate: () => void;
    }> = {},
  ): void {
    render(() => (
      <ImportFooter
        missingSource={overrides.missingSource ?? null}
        nothingChosen={overrides.nothingChosen ?? false}
        isReviewing={overrides.isReviewing ?? false}
        isExtracting={overrides.isExtracting ?? false}
        uploadableFile={overrides.uploadableFile ?? null}
        onCancel={overrides.onCancel ?? vi.fn()}
        onUploadOnly={overrides.onUploadOnly ?? vi.fn()}
        onContinue={overrides.onContinue ?? vi.fn()}
        onGenerate={overrides.onGenerate ?? vi.fn()}
      />
    ));
  }

  it("continues once a source is there", () => {
    const onContinue = vi.fn();
    renderFooter({ onContinue });

    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    expect(onContinue).toHaveBeenCalledTimes(1);
  });

  it("says what the source is missing and blocks continuing", () => {
    renderFooter({ missingSource: "Choose a file first." });

    expect(document.querySelector(".modal-foot-hint")?.textContent).toBe(
      "Choose a file first.",
    );
    expect(screen.getByRole("button", { name: "Continue" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("blocks continuing while the text is being read", () => {
    renderFooter({ isExtracting: true });

    expect(screen.getByRole("button", { name: "Continue" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("offers upload only for a file", () => {
    const onUploadOnly = vi.fn();
    const chosen = pdfFile();
    renderFooter({ uploadableFile: chosen, onUploadOnly });

    fireEvent.click(screen.getByRole("button", { name: "Upload only" }));

    expect(onUploadOnly).toHaveBeenCalledWith(chosen);
  });

  it("blocks upload only while the text is being read", () => {
    renderFooter({ uploadableFile: pdfFile(), isExtracting: true });

    expect(screen.getByRole("button", { name: "Upload only" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("generates once the review is showing", () => {
    const onGenerate = vi.fn();
    renderFooter({ isReviewing: true, onGenerate });

    fireEvent.click(screen.getByRole("button", { name: "Generate" }));

    expect(onGenerate).toHaveBeenCalledTimes(1);
  });

  it("blocks generating when nothing was chosen", () => {
    renderFooter({ isReviewing: true, nothingChosen: true });

    expect(screen.getByRole("button", { name: "Generate" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("cancels the import", () => {
    const onCancel = vi.fn();
    renderFooter({ onCancel });

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
