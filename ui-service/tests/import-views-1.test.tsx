import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { ImportButton } from "../src/features/folder/import/ImportButton";
import { PdfPageRange } from "../src/features/folder/import/PdfPageRange";
import { TypeCount } from "../src/features/folder/import/TypeCount";
import "./import-views-support";

describe("ImportButton", () => {
  it("dresses itself for where it stands", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("toolbar", "empty-state" as const),
        (variant) => {
          const { unmount } = render(() => (
            <ImportButton variant={variant} onOpen={vi.fn()} />
          ));

          expect(
            screen
              .getByRole("button", { name: "Import" })
              .className.includes("btn-lg"),
          ).toBe(variant === "empty-state");
          unmount();
        },
      ),
    );
  });

  it("opens the import flow when pressed", () => {
    const onOpen = vi.fn();
    render(() => <ImportButton variant="toolbar" onOpen={onOpen} />);

    fireEvent.click(screen.getByRole("button", { name: "Import" }));

    expect(onOpen).toHaveBeenCalledTimes(1);
  });
});

describe("PdfPageRange", () => {
  it("reports both ends of the range", () => {
    const onFirstPageChange = vi.fn();
    const onLastPageChange = vi.fn();
    render(() => (
      <PdfPageRange
        firstPage=""
        lastPage=""
        onFirstPageChange={onFirstPageChange}
        onLastPageChange={onLastPageChange}
      />
    ));

    fireEvent.input(screen.getByLabelText("First page"), {
      target: { value: "2" },
    });
    fireEvent.input(screen.getByLabelText("Last page"), {
      target: { value: "9" },
    });

    expect(onFirstPageChange).toHaveBeenCalledWith("2");
    expect(onLastPageChange).toHaveBeenCalledWith("9");
  });
});

describe("TypeCount", () => {
  function renderCount(
    count: number | null,
    isCustom: boolean,
    onChoose = vi.fn(),
    onCustom = vi.fn(),
  ): void {
    render(() => (
      <TypeCount
        name="flashcards-basic"
        count={count}
        isCustom={isCustom}
        onChoose={onChoose}
        onCustom={onCustom}
      />
    ));
  }

  it("marks Auto when no count was chosen", () => {
    renderCount(null, false);

    expect(screen.getByLabelText("Auto")).toHaveProperty("checked", true);
  });

  it("marks the preset already chosen", () => {
    fc.assert(
      fc.property(fc.constantFrom(10, 20), (preset) => {
        const { unmount } = render(() => (
          <TypeCount
            name="flashcards-basic"
            count={preset}
            isCustom={false}
            onChoose={vi.fn()}
            onCustom={vi.fn()}
          />
        ));

        expect(screen.getByLabelText(String(preset))).toHaveProperty(
          "checked",
          true,
        );
        unmount();
      }),
    );
  });

  it("chooses Auto again", () => {
    const onChoose = vi.fn();
    renderCount(10, false, onChoose);

    fireEvent.change(screen.getByLabelText("Auto"));

    expect(onChoose).toHaveBeenCalledWith(null);
  });

  it("chooses a preset count", () => {
    const onChoose = vi.fn();
    renderCount(null, false, onChoose);

    fireEvent.change(screen.getByLabelText("20"));

    expect(onChoose).toHaveBeenCalledWith(20);
  });

  it("asks for a custom count", () => {
    const onCustom = vi.fn();
    renderCount(null, false, vi.fn(), onCustom);

    fireEvent.change(screen.getByLabelText("Custom"));

    expect(onCustom).toHaveBeenCalledTimes(1);
    expect(screen.queryByLabelText("How many for flashcards-basic")).toBeNull();
  });

  it("takes a custom count once it is asked for", () => {
    const onChoose = vi.fn();
    renderCount(null, true, onChoose);

    fireEvent.input(screen.getByLabelText("How many for flashcards-basic"), {
      target: { value: "37" },
    });

    expect(onChoose).toHaveBeenCalledWith(37);
  });

  it("reads a cleared custom count as none at all", () => {
    const onChoose = vi.fn();
    renderCount(7, true, onChoose);

    fireEvent.input(screen.getByLabelText("How many for flashcards-basic"), {
      target: { value: "" },
    });

    expect(onChoose).toHaveBeenCalledWith(null);
  });

  it("shows the custom count it already carries", () => {
    renderCount(37, true);

    expect(
      screen.getByLabelText("How many for flashcards-basic"),
    ).toHaveProperty("value", "37");
  });
});
