import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import { TestItemActions } from "../src/features/assessment/TestItemActions";
import { MULTIPLE_CHOICE } from "./assessment-views-support";

describe("TestItemActions", () => {
  it("opens the editor from its own menu and saves through it", () => {
    const onSave = vi.fn();
    render(() => <TestItemActions item={MULTIPLE_CHOICE} onSave={onSave} />);

    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this question" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Edit question" }));
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onSave).toHaveBeenCalledTimes(1);
    expect(document.querySelector(".modal")).toBeNull();
  });

  it("closes the editor when it is cancelled", () => {
    render(() => <TestItemActions item={MULTIPLE_CHOICE} onSave={vi.fn()} />);

    fireEvent.click(
      screen.getByRole("button", { name: "Actions for this question" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Edit question" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(document.querySelector(".modal")).toBeNull();
  });
});
