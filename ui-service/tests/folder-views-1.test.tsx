import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { DueSection } from "../src/features/folder/DueSection";
import { UnitListSkeleton } from "../src/features/folder/UnitListSkeleton";
import { COUNT, breakdownOf } from "./folder-views-support";

describe("DueMath.totalDue", () => {
  it("totalDue property counts every kind of due work together", () => {
    fc.assert(
      fc.property(COUNT, COUNT, COUNT, (flashcards, testItems, notes) => {
        const total = flashcards + testItems + notes;
        const { unmount } = render(() => (
          <DueSection
            breakdown={breakdownOf(flashcards, testItems, notes)}
            onReviewFlashcards={vi.fn()}
            onReviewTest={vi.fn()}
          />
        ));

        if (total > 0) {
          expect(
            screen.getByRole("button", { name: `Review ${total} items` }),
          ).toBeTruthy();
        } else {
          expect(document.querySelector(".due-action")).toBeNull();
        }

        unmount();
      }),
      { numRuns: 12 },
    );
  });
});

describe("DueSection", () => {
  it("counts what is done out of today's total", () => {
    render(() => (
      <DueSection
        breakdown={breakdownOf(1, 2, 3)}
        onReviewFlashcards={vi.fn()}
        onReviewTest={vi.fn()}
      />
    ));

    expect(document.querySelector(".due-progress")?.textContent).toBe(
      "2 of 8 done",
    );
  });

  it("mutes a kind with nothing due", () => {
    render(() => (
      <DueSection
        breakdown={breakdownOf(0, 2, 0)}
        onReviewFlashcards={vi.fn()}
        onReviewTest={vi.fn()}
      />
    ));
    const items = [...document.querySelectorAll(".due-item")];

    expect(items.map((item) => item.className.includes("is-clear"))).toEqual([
      true,
      false,
      true,
    ]);
  });

  it("starts the flashcard review that was chosen", () => {
    const onReviewFlashcards = vi.fn();
    render(() => (
      <DueSection
        breakdown={breakdownOf(3, 1, 0)}
        onReviewFlashcards={onReviewFlashcards}
        onReviewTest={vi.fn()}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Review 4 items" }));
    fireEvent.click(screen.getByRole("menuitem", { name: /^Flashcards/ }));

    expect(onReviewFlashcards).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("menu")).toBeNull();
  });

  it("starts the test review that was chosen", () => {
    const onReviewTest = vi.fn();
    render(() => (
      <DueSection
        breakdown={breakdownOf(3, 1, 0)}
        onReviewFlashcards={vi.fn()}
        onReviewTest={onReviewTest}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Review 4 items" }));
    fireEvent.click(screen.getByRole("menuitem", { name: /^Test/ }));

    expect(onReviewTest).toHaveBeenCalledTimes(1);
  });

  it("closes its own menu when dismissed", () => {
    render(() => (
      <DueSection
        breakdown={breakdownOf(1, 0, 0)}
        onReviewFlashcards={vi.fn()}
        onReviewTest={vi.fn()}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Review 1 items" }));
    fireEvent.mouseDown(document.body);

    expect(screen.queryByRole("menu")).toBeNull();
  });
});

describe("UnitListSkeleton", () => {
  it("stands in for the list while it loads", () => {
    render(() => <UnitListSkeleton />);

    expect(
      document.querySelector(".skeleton-list")?.getAttribute("aria-busy"),
    ).toBe("true");
    expect(document.querySelectorAll(".skeleton-row")).toHaveLength(4);
  });
});
