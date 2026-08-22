import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { AccountApi } from "../src/features/settings/account-api";
import { AssessmentApi } from "../src/features/assessment/assessment-api";
import AssessmentPage from "../src/features/assessment/AssessmentPage";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import { renderAt } from "./router-support";
import { pageOf } from "./assessment-views-support";

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
