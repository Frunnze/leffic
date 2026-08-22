import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { ModalBackdrop } from "../src/shared/ui/ModalBackdrop";
import { ReviewBar } from "../src/shared/ui/ReviewBar";
import { LABEL } from "./shared-ui-support";

describe("ModalBackdrop", () => {
  it("dismisses when the backdrop itself is clicked", () => {
    const onDismiss = vi.fn();
    render(() => (
      <ModalBackdrop onDismiss={onDismiss}>
        <div data-testid="panel" />
      </ModalBackdrop>
    ));

    fireEvent.click(document.querySelector(".modal-backdrop") as HTMLElement);

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("stays open when the dialog inside it is clicked", () => {
    const onDismiss = vi.fn();
    render(() => (
      <ModalBackdrop onDismiss={onDismiss}>
        <div data-testid="panel" />
      </ModalBackdrop>
    ));

    fireEvent.click(screen.getByTestId("panel"));

    expect(onDismiss).not.toHaveBeenCalled();
  });

  it("dismisses on the escape key", () => {
    const onDismiss = vi.fn();
    render(() => <ModalBackdrop onDismiss={onDismiss}>{null}</ModalBackdrop>);

    fireEvent.keyDown(document, { key: "Escape" });

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("ignores every other key", () => {
    const onDismiss = vi.fn();
    render(() => <ModalBackdrop onDismiss={onDismiss}>{null}</ModalBackdrop>);

    fireEvent.keyDown(document, { key: "Enter" });

    expect(onDismiss).not.toHaveBeenCalled();
  });

  it("stops listening once the dialog is gone", () => {
    const onDismiss = vi.fn();
    const { unmount } = render(() => (
      <ModalBackdrop onDismiss={onDismiss}>{null}</ModalBackdrop>
    ));

    unmount();
    fireEvent.keyDown(document, { key: "Escape" });

    expect(onDismiss).not.toHaveBeenCalled();
  });
});

describe("ReviewBar", () => {
  it("names what is under review in its close button", () => {
    fc.assert(
      fc.property(LABEL, (title) => {
        const { unmount } = render(() => (
          <ReviewBar title={title} onClose={() => undefined} />
        ));

        expect(
          screen.getByRole("button", { name: `Close ${title}` }),
        ).toBeTruthy();
        unmount();
      }),
    );
  });

  it("closes the review when asked", () => {
    const onClose = vi.fn();
    render(() => <ReviewBar title="Deck" onClose={onClose} />);

    fireEvent.click(screen.getByRole("button", { name: "Close Deck" }));

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
