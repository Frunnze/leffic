import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import { TestItemEditor } from "../src/features/assessment/TestItemEditor";
import { MULTIPLE_CHOICE } from "./assessment-views-support";

describe("TestItemEditor", () => {
  function renderEditor(onSave = vi.fn()): void {
    render(() => (
      <TestItemEditor
        item={MULTIPLE_CHOICE}
        onSave={onSave}
        onCancel={vi.fn()}
      />
    ));
  }

  it("starts from the question and answers it was given", () => {
    renderEditor();

    expect(screen.getByLabelText("Question")).toHaveProperty(
      "value",
      MULTIPLE_CHOICE.question,
    );
    expect(screen.getByLabelText("Answer 1")).toHaveProperty(
      "value",
      "Rayleigh scattering",
    );
  });

  it("saves the edited question and its answers", () => {
    const onSave = vi.fn();
    renderEditor(onSave);

    fireEvent.input(screen.getByLabelText("Question"), {
      target: { value: " Why is it blue? " },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).toHaveBeenCalledWith({
      question: "Why is it blue?",
      correctAnswer: "Rayleigh scattering",
      wrongAnswers: ["Reflected ocean"],
    });
  });

  it("adds an answer and refuses to save while it is blank", () => {
    const onSave = vi.fn();
    renderEditor(onSave);

    fireEvent.click(screen.getByRole("button", { name: "Add answer" }));
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(screen.getByLabelText("Answer 3")).toBeTruthy();
    expect(onSave).not.toHaveBeenCalled();
  });

  it("refuses to save a blank question", () => {
    const onSave = vi.fn();
    renderEditor(onSave);

    fireEvent.input(screen.getByLabelText("Question"), {
      target: { value: "   " },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).not.toHaveBeenCalled();
  });

  it("edits an answer in place", () => {
    const onSave = vi.fn();
    renderEditor(onSave);

    fireEvent.input(screen.getByLabelText("Answer 2"), {
      target: { value: "Refracted light" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({ wrongAnswers: ["Refracted light"] }),
    );
  });

  it("marks a different answer as the correct one", () => {
    const onSave = vi.fn();
    renderEditor(onSave);

    fireEvent.change(
      screen.getByLabelText('Mark "Reflected ocean" as the correct answer'),
    );
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({
        correctAnswer: "Reflected ocean",
        wrongAnswers: ["Rayleigh scattering"],
      }),
    );
  });

  it("removes an answer and keeps the correct one in step", () => {
    const onSave = vi.fn();
    renderEditor(onSave);

    fireEvent.change(
      screen.getByLabelText('Mark "Reflected ocean" as the correct answer'),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Remove Rayleigh scattering" }),
    );
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).toHaveBeenCalledWith({
      question: MULTIPLE_CHOICE.question,
      correctAnswer: "Reflected ocean",
      wrongAnswers: [],
    });
  });

  it("keeps the first answer correct when it is the one removed", () => {
    const onSave = vi.fn();
    renderEditor(onSave);

    fireEvent.click(
      screen.getByRole("button", { name: "Remove Rayleigh scattering" }),
    );
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({ correctAnswer: "Reflected ocean" }),
    );
  });

  it("saves an empty answer when every answer was removed", () => {
    const onSave = vi.fn();
    renderEditor(onSave);

    fireEvent.click(
      screen.getByRole("button", { name: "Remove Rayleigh scattering" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Remove Reflected ocean" }),
    );
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).toHaveBeenCalledWith({
      question: MULTIPLE_CHOICE.question,
      correctAnswer: "",
      wrongAnswers: [],
    });
  });

  it("cancels from the backdrop", () => {
    const onCancel = vi.fn();
    render(() => (
      <TestItemEditor
        item={MULTIPLE_CHOICE}
        onSave={vi.fn()}
        onCancel={onCancel}
      />
    ));

    fireEvent.click(document.querySelector(".modal-backdrop") as HTMLElement);

    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("cancels from the head", () => {
    const onCancel = vi.fn();
    render(() => (
      <TestItemEditor
        item={MULTIPLE_CHOICE}
        onSave={vi.fn()}
        onCancel={onCancel}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Close dialog" }));

    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
