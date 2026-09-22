import { describe, expect, it, vi } from "vitest";
import {
  fireEvent,
  render,
  screen,
  waitFor,
} from "@solidjs/testing-library";
import { AccountApi } from "../src/features/settings/account-api";
import { AssessmentApi } from "../src/features/assessment/assessment-api";
import AssessmentPage from "../src/features/assessment/AssessmentPage";
import { AssessmentReview } from "../src/features/assessment/AssessmentReview";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import { renderAt } from "./router-support";
import {
  MULTIPLE_CHOICE,
  SHORT_ANSWER,
  pageOf,
} from "./assessment-views-support";

describe("AssessmentPage", () => {
  it("frames the review inside the app shell", async () => {
    vi.spyOn(AccountApi, "read").mockResolvedValue({
      username: "learner",
      email: "learner@example.test",
      theme: "system",
    });
    vi.spyOn(AssessmentApi, "page").mockResolvedValue(pageOf([], 1, 0));
    renderAt("/test/7", "/test/:id", () => (
      <AskProvider>
        <AssessmentPage scope="test" />
      </AskProvider>
    ));

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Close Test" })).toBeTruthy(),
    );

    fireEvent.click(screen.getByRole("button", { name: "Close Test" }));

    expect(document.querySelector(".review-page")).toBeTruthy();
  });
});

describe("AssessmentReview with the progress memory it is given", () => {
  it("resumes and remembers through that memory alone", async () => {
    const progress = {
      storedPage: vi.fn(() => 2),
      storedIndex: vi.fn(() => 0),
      remember: vi.fn(),
      forget: vi.fn(),
    };
    const paging = vi
      .spyOn(AssessmentApi, "page")
      .mockResolvedValue(pageOf([MULTIPLE_CHOICE, SHORT_ANSWER], 2, 4));
    render(() => (
      <AssessmentReview scope="test" scopeId="7" progress={progress} />
    ));

    await waitFor(() => screen.getByRole("button", { name: "Next" }));
    fireEvent.click(screen.getByRole("button", { name: "Next" }));

    await waitFor(() =>
      expect(progress.remember).toHaveBeenCalledWith("7", 2, 1),
    );
    expect(paging).toHaveBeenCalledWith("test", "7", 2);
    expect(localStorage.getItem("testLastIndex7")).toBeNull();
  });
});
