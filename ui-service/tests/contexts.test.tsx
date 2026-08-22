import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { AskProvider, useAsk } from "../src/shared/chatbot/AskContext";
import {
  ToastProvider,
  useToasts,
} from "../src/shared/notifications/ToastContext";
import { Toasts } from "../src/shared/notifications/Toasts";

function AskOpener(): ReturnType<typeof useAsk> extends never
  ? never
  : import("solid-js").JSX.Element {
  const ask = useAsk();

  return (
    <button
      type="button"
      onClick={() => {
        ask.toggle();
      }}
    >
      {ask.isOpen() ? "open" : "closed"}
    </button>
  );
}

function ToastRaiser(): import("solid-js").JSX.Element {
  const toasts = useToasts();

  return (
    <>
      <button
        type="button"
        onClick={() => {
          toasts.show({ tone: "success", title: "Saved" });
        }}
      >
        raise
      </button>
      <Toasts toasts={toasts.toasts()} onDismiss={toasts.dismiss} />
    </>
  );
}

describe("useAsk", () => {
  it("useAsk property gives every reader the same store", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 5 }), (toggles) => {
        const { unmount } = render(() => (
          <AskProvider>
            <AskOpener />
            <AskOpener />
          </AskProvider>
        ));
        const [first] = screen.getAllByRole("button");

        for (let count = 0; count < toggles; count += 1) {
          fireEvent.click(first as HTMLElement);
        }

        const shown = screen
          .getAllByRole("button")
          .map((button) => button.textContent);

        expect(new Set(shown).size).toBe(1);
        unmount();
      }),
      { numRuns: 5 },
    );
  });

  it("refuses to be read outside a provider", () => {
    expect(() => render(() => <AskOpener />)).toThrow(
      "useAsk must be used inside an AskProvider",
    );
  });
});

describe("useToasts", () => {
  it("useToasts property shows every toast raised through it", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 4 }), (count) => {
        const { unmount } = render(() => (
          <ToastProvider>
            <ToastRaiser />
          </ToastProvider>
        ));

        for (let raised = 0; raised < count; raised += 1) {
          fireEvent.click(screen.getByRole("button", { name: "raise" }));
        }

        expect(document.querySelectorAll(".toast")).toHaveLength(count);
        unmount();
      }),
      { numRuns: 4 },
    );
  });

  it("refuses to be read outside a provider", () => {
    expect(() => render(() => <ToastRaiser />)).toThrow(
      "useToasts must be used inside a ToastProvider",
    );
  });
});

describe("Toasts", () => {
  it("shows nothing at all when nothing was raised", () => {
    render(() => <Toasts toasts={[]} onDismiss={() => undefined} />);

    expect(document.querySelector(".toast-stack")).toBeNull();
  });

  it.each([
    ["progress", "toast-progress"],
    ["success", "toast-success"],
    ["failure", "toast-failure"],
  ] as const)("dresses a %s toast in its own tone", (tone, className) => {
    render(() => (
      <Toasts
        toasts={[{ id: "1", tone, title: "Working" }]}
        onDismiss={() => undefined}
      />
    ));

    expect(document.querySelector(".toast")?.className).toContain(className);
  });

  it("shows the detail when a toast carries one", () => {
    render(() => (
      <Toasts
        toasts={[{ id: "1", tone: "failure", title: "Failed", detail: "why" }]}
        onDismiss={() => undefined}
      />
    ));

    expect(document.querySelector(".toast-detail")?.textContent).toBe("why");
  });

  it("shows no detail line when a toast carries none", () => {
    render(() => (
      <Toasts
        toasts={[{ id: "1", tone: "success", title: "Saved" }]}
        onDismiss={() => undefined}
      />
    ));

    expect(document.querySelector(".toast-detail")).toBeNull();
  });

  it("dismisses exactly the toast whose button was pressed", () => {
    const onDismiss = vi.fn();
    render(() => (
      <Toasts
        toasts={[{ id: "abc", tone: "success", title: "Saved" }]}
        onDismiss={onDismiss}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: 'Dismiss "Saved"' }));

    expect(onDismiss).toHaveBeenCalledWith("abc");
  });
});
