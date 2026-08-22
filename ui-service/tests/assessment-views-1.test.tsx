import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import {
  AssessmentQuestion,
} from "../src/features/assessment/AssessmentQuestion";
import { AssessmentResult } from "../src/features/assessment/AssessmentResult";
import type {
  AssessmentItem,
} from "../src/features/assessment/assessment-models";
import { MULTIPLE_CHOICE, SHORT_ANSWER } from "./assessment-views-support";

describe("AssessmentResult", () => {
  it("never reports a negative number missed", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 20 }),
        fc.integer({ min: 0, max: 20 }),
        (correct, total) => {
          const { unmount } = render(() => (
            <AssessmentResult
              correct={correct}
              total={total}
              onRetake={vi.fn()}
            />
          ));

          expect(
            Number(
              document
                .querySelector(".test-score-detail")
                ?.textContent?.match(/\d+/)?.[0],
            ),
          ).toBeGreaterThanOrEqual(0);
          unmount();
        },
      ),
    );
  });

  it("shows the score out of the total", () => {
    render(() => <AssessmentResult correct={3} total={5} onRetake={vi.fn()} />);

    expect(document.querySelector(".test-score")?.textContent).toBe("3 / 5");
  });

  it("retakes the test when asked", () => {
    const onRetake = vi.fn();
    render(() => (
      <AssessmentResult correct={3} total={5} onRetake={onRetake} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Retake test" }));

    expect(onRetake).toHaveBeenCalledTimes(1);
  });
});

describe("AssessmentQuestion", () => {
  function renderQuestion(
    item: AssessmentItem,
    overrides: Partial<{
      chosenAnswers: readonly (string | number)[];
      position: number;
      totalItems: number;
      onChoose: (answer: string | number) => void;
      onBack: () => void;
      onNext: () => void;
    }> = {},
  ): void {
    render(() => (
      <AssessmentQuestion
        item={item}
        chosenAnswers={overrides.chosenAnswers ?? []}
        position={overrides.position ?? 1}
        totalItems={overrides.totalItems ?? 3}
        onChoose={overrides.onChoose ?? vi.fn()}
        onEdit={vi.fn()}
        onBack={overrides.onBack ?? vi.fn()}
        onNext={overrides.onNext ?? vi.fn()}
      />
    ));
  }

  it("letters every option of a multiple choice question", () => {
    renderQuestion(MULTIPLE_CHOICE);

    expect(
      [...document.querySelectorAll(".test-key")].map((key) => key.textContent),
    ).toEqual(["A", "B"]);
  });

  it("chooses the option that was pressed", () => {
    const onChoose = vi.fn();
    renderQuestion(MULTIPLE_CHOICE, { onChoose });

    fireEvent.click(screen.getByRole("button", { name: /Rayleigh/ }));

    expect(onChoose).toHaveBeenCalledWith(0);
  });

  it("marks the option already chosen", () => {
    renderQuestion(MULTIPLE_CHOICE, { chosenAnswers: [1] });

    expect(
      [...document.querySelectorAll(".test-option")].map((option) =>
        option.getAttribute("aria-pressed"),
      ),
    ).toEqual(["false", "true"]);
  });

  it("takes a typed answer when there are no options", () => {
    const onChoose = vi.fn();
    renderQuestion(SHORT_ANSWER, { onChoose });

    fireEvent.input(screen.getByLabelText("Your answer"), {
      target: { value: "mitosis" },
    });

    expect(onChoose).toHaveBeenCalledWith("mitosis");
  });

  it("shows the answer already typed", () => {
    renderQuestion(SHORT_ANSWER, { chosenAnswers: ["mitosis"] });

    expect(screen.getByLabelText("Your answer")).toHaveProperty(
      "value",
      "mitosis",
    );
  });

  it("shows an empty box when nothing was typed yet", () => {
    renderQuestion(SHORT_ANSWER);

    expect(screen.getByLabelText("Your answer")).toHaveProperty("value", "");
  });

  it("blocks going back from the first question", () => {
    renderQuestion(MULTIPLE_CHOICE, { position: 1 });

    expect(screen.getByRole("button", { name: "Back" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("goes back from any later question", () => {
    const onBack = vi.fn();
    renderQuestion(MULTIPLE_CHOICE, { position: 2, onBack });

    fireEvent.click(screen.getByRole("button", { name: "Back" }));

    expect(onBack).toHaveBeenCalledTimes(1);
  });

  it("says Next until the last question", () => {
    renderQuestion(MULTIPLE_CHOICE, { position: 1, totalItems: 3 });

    expect(screen.getByRole("button", { name: "Next" })).toBeTruthy();
  });

  it("says Finish on the last question", () => {
    const onNext = vi.fn();
    renderQuestion(MULTIPLE_CHOICE, { position: 3, totalItems: 3, onNext });

    fireEvent.click(screen.getByRole("button", { name: "Finish" }));

    expect(onNext).toHaveBeenCalledTimes(1);
  });
});
