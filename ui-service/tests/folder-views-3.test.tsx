import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { MoveUnitDialog } from "../src/features/folder/MoveUnitDialog";
import { unitOf } from "./unit-factories";
import "./folder-views-support";

describe("MoveUnitDialog", () => {
  it("offers every destination it was given", () => {
    fc.assert(
      fc.property(
        fc.array(fc.stringMatching(/^[A-Za-z]{1,8}$/), { maxLength: 3 }),
        (names) => {
          const destinations = names.map((name, index) => ({
            id: String(index),
            name,
          }));
          const { unmount } = render(() => (
            <MoveUnitDialog
              unit={unitOf({ name: "Note" })}
              destinations={destinations}
              onConfirm={vi.fn()}
              onCancel={vi.fn()}
            />
          ));

          expect(screen.queryAllByRole("radio")).toHaveLength(
            destinations.length,
          );
          unmount();
        },
      ),
    );
  });

  it("moves the unit into the folder that was picked", () => {
    const onConfirm = vi.fn();
    render(() => (
      <MoveUnitDialog
        unit={unitOf({ name: "Note" })}
        destinations={[
          { id: "home", name: "Home" },
          { id: "biology", name: "Biology" },
        ]}
        onConfirm={onConfirm}
        onCancel={vi.fn()}
      />
    ));

    fireEvent.change(screen.getByLabelText("Biology"));
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onConfirm).toHaveBeenCalledWith("biology");
  });

  it("moves into the home folder by default", () => {
    const onConfirm = vi.fn();
    render(() => (
      <MoveUnitDialog
        unit={unitOf({ name: "Note" })}
        destinations={[{ id: "home", name: "Home" }]}
        onConfirm={onConfirm}
        onCancel={vi.fn()}
      />
    ));

    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onConfirm).toHaveBeenCalledWith("home");
  });

  it("cancels from the footer", () => {
    const onCancel = vi.fn();
    render(() => (
      <MoveUnitDialog
        unit={unitOf({ name: "Note" })}
        destinations={[]}
        onConfirm={vi.fn()}
        onCancel={onCancel}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    fireEvent.click(screen.getByRole("button", { name: "Close dialog" }));
    fireEvent.click(document.querySelector(".modal-backdrop") as HTMLElement);

    expect(onCancel).toHaveBeenCalledTimes(3);
  });
});
