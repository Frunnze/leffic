import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { PromptDialog } from "../src/shared/ui/PromptDialog";
import "./folder-views-support";

describe("PromptDialog", () => {
  it("confirms the trimmed text that was typed", () => {
    fc.assert(
      fc.property(
        fc.stringMatching(/^[A-Za-z][A-Za-z ]{0,8}[A-Za-z]$/),
        (typed) => {
          const onConfirm = vi.fn();
          const { unmount } = render(() => (
            <PromptDialog
              title="Rename"
              description="Pick a name"
              label="Name"
              placeholder="name"
              inputType="text"
              confirmLabel="Save"
              onConfirm={onConfirm}
              onCancel={vi.fn()}
            />
          ));

          fireEvent.input(screen.getByLabelText("Name"), {
            target: { value: ` ${typed} ` },
          });
          fireEvent.submit(document.querySelector("form") as HTMLFormElement);

          expect(onConfirm).toHaveBeenCalledWith(typed.trim());
          unmount();
        },
      ),
    );
  });

  it("blocks the confirm button until something is typed", () => {
    render(() => (
      <PromptDialog
        title="Rename"
        description="d"
        label="Name"
        placeholder="p"
        inputType="text"
        confirmLabel="Save"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
      />
    ));

    expect(screen.getByRole("button", { name: "Save" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("refuses to confirm blank text", () => {
    const onConfirm = vi.fn();
    render(() => (
      <PromptDialog
        title="Rename"
        description="d"
        label="Name"
        placeholder="p"
        inputType="text"
        confirmLabel="Save"
        onConfirm={onConfirm}
        onCancel={vi.fn()}
      />
    ));

    fireEvent.input(screen.getByLabelText("Name"), {
      target: { value: "   " },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onConfirm).not.toHaveBeenCalled();
  });

  it("dresses a dangerous confirmation in its own tone", () => {
    render(() => (
      <PromptDialog
        title="Delete"
        description="d"
        label="Password"
        placeholder="p"
        inputType="password"
        confirmLabel="Delete"
        confirmTone="danger"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
      />
    ));

    expect(screen.getByRole("button", { name: "Delete" }).className).toContain(
      "btn-danger",
    );
  });

  it("cancels from the footer, the head and the backdrop", () => {
    const onCancel = vi.fn();
    render(() => (
      <PromptDialog
        title="Rename"
        description="d"
        label="Name"
        placeholder="p"
        inputType="text"
        confirmLabel="Save"
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
