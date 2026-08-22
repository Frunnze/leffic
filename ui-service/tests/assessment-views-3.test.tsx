import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@solidjs/testing-library";
import { AssessmentApi } from "../src/features/assessment/assessment-api";
import { AssessmentReview } from "../src/features/assessment/AssessmentReview";
import {
  MULTIPLE_CHOICE,
  SHORT_ANSWER,
  pageOf,
} from "./assessment-views-support";

describe("AssessmentReview", () => {
  function renderReview(): void {
    render(() => <AssessmentReview scope="test" scopeId="7" />);
  }

  it("says so when the test has no questions yet", async () => {
    vi.spyOn(AssessmentApi, "page").mockResolvedValue(pageOf([], 1, 0));
    renderReview();

    await waitFor(() =>
      expect(document.querySelector(".state-title")?.textContent).toBe(
        "This test has no questions yet",
      ),
    );
  });

  it("shows the first question of the stored page", async () => {
    vi.spyOn(AssessmentApi, "page").mockResolvedValue(
      pageOf([MULTIPLE_CHOICE, SHORT_ANSWER]),
    );
    renderReview();

    await waitFor(() =>
      expect(document.querySelector(".test-question")?.textContent).toBe(
        MULTIPLE_CHOICE.question,
      ),
    );
  });

  it("moves to the next question and remembers where it is", async () => {
    vi.spyOn(AssessmentApi, "page").mockResolvedValue(
      pageOf([MULTIPLE_CHOICE, SHORT_ANSWER], 1, 4),
    );
    const submitting = vi
      .spyOn(AssessmentApi, "submitAnswer")
      .mockResolvedValue(undefined);
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: /Rayleigh/ }));
    fireEvent.click(screen.getByRole("button", { name: /Rayleigh/ }));
    fireEvent.click(screen.getByRole("button", { name: "Next" }));

    await waitFor(() =>
      expect(document.querySelector(".test-question")?.textContent).toBe(
        SHORT_ANSWER.question,
      ),
    );
    expect(submitting).toHaveBeenCalledWith("1", "session", [0]);
    expect(localStorage.getItem("testLastIndex7")).toBe("1");
  });

  it("loads the next page once the current one runs out", async () => {
    const paging = vi
      .spyOn(AssessmentApi, "page")
      .mockResolvedValueOnce(pageOf([MULTIPLE_CHOICE], 1, 4))
      .mockResolvedValueOnce(pageOf([SHORT_ANSWER], 2, 4));
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: "Next" }));
    fireEvent.click(screen.getByRole("button", { name: "Next" }));

    await waitFor(() => expect(paging).toHaveBeenCalledTimes(2));
    expect(localStorage.getItem("testPage7")).toBe("2");
  });

  it("finishes the test and shows the score", async () => {
    vi.spyOn(AssessmentApi, "page").mockResolvedValue(
      pageOf([MULTIPLE_CHOICE], 1, 1),
    );
    vi.spyOn(AssessmentApi, "sessionResult").mockResolvedValue({ correct: 1 });
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: "Finish" }));
    fireEvent.click(screen.getByRole("button", { name: "Finish" }));

    await waitFor(() =>
      expect(document.querySelector(".test-score")?.textContent).toBe("1 / 1"),
    );
    expect(localStorage.getItem("testPage7")).toBeNull();
  });

  it("counts nothing correct when the session cannot be read", async () => {
    vi.spyOn(AssessmentApi, "page").mockResolvedValue(
      pageOf([MULTIPLE_CHOICE], 1, 1),
    );
    vi.spyOn(AssessmentApi, "sessionResult").mockResolvedValue(null);
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: "Finish" }));
    fireEvent.click(screen.getByRole("button", { name: "Finish" }));

    await waitFor(() =>
      expect(document.querySelector(".test-score")?.textContent).toBe("0 / 1"),
    );
  });

  it("retakes the test from the first question", async () => {
    const paging = vi
      .spyOn(AssessmentApi, "page")
      .mockResolvedValue(pageOf([MULTIPLE_CHOICE], 1, 1));
    vi.spyOn(AssessmentApi, "sessionResult").mockResolvedValue({ correct: 0 });
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: "Finish" }));
    fireEvent.click(screen.getByRole("button", { name: "Finish" }));
    await waitFor(() => screen.getByRole("button", { name: "Retake test" }));
    fireEvent.click(screen.getByRole("button", { name: "Retake test" }));

    await waitFor(() => expect(paging).toHaveBeenCalledTimes(2));
  });

  it("goes back to the previous question", async () => {
    vi.spyOn(AssessmentApi, "page").mockResolvedValue(
      pageOf([MULTIPLE_CHOICE, SHORT_ANSWER], 1, 4),
    );
    localStorage.setItem("testLastIndex7", "1");
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: "Back" }));
    fireEvent.click(screen.getByRole("button", { name: "Back" }));

    await waitFor(() =>
      expect(document.querySelector(".test-question")?.textContent).toBe(
        MULTIPLE_CHOICE.question,
      ),
    );
  });

  it("goes back into the previous page", async () => {
    const paging = vi
      .spyOn(AssessmentApi, "page")
      .mockResolvedValueOnce(pageOf([SHORT_ANSWER], 2, 4))
      .mockResolvedValueOnce(pageOf([MULTIPLE_CHOICE], 1, 4));
    localStorage.setItem("testPage7", "2");
    renderReview();

    await waitFor(() => screen.getByRole("button", { name: "Back" }));
    fireEvent.click(screen.getByRole("button", { name: "Back" }));

    await waitFor(() => expect(paging).toHaveBeenCalledTimes(2));
  });

  it("keeps an answer the learner gave before", async () => {
    vi.spyOn(AssessmentApi, "page").mockResolvedValue(
      pageOf([{ ...MULTIPLE_CHOICE, lastAnswers: [1] }], 1, 1),
    );
    renderReview();

    await waitFor(() =>
      expect(
        [...document.querySelectorAll(".test-option")].map((option) =>
          option.getAttribute("aria-pressed"),
        ),
      ).toEqual(["false", "true"]),
    );
  });

  it("saves an edited question and reloads the page", async () => {
    const paging = vi
      .spyOn(AssessmentApi, "page")
      .mockResolvedValue(pageOf([MULTIPLE_CHOICE], 1, 1));
    const updating = vi
      .spyOn(AssessmentApi, "updateItem")
      .mockResolvedValue(undefined);
    renderReview();

    await waitFor(() =>
      screen.getByRole("button", { name: "Actions for this question" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this question" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Edit question" }));
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() => expect(updating).toHaveBeenCalledTimes(1));
    expect(paging).toHaveBeenCalledTimes(2);
  });
});
