import { describe, expect, it } from "vitest";
import { createRoot } from "solid-js";
import fc from "fast-check";
import {
  AskStoreFactory,
  type AskStore,
} from "../src/shared/chatbot/ask-store";

function withStore<T>(use: (store: AskStore) => T): T {
  return createRoot((dispose) => {
    const outcome = use(AskStoreFactory.create());
    dispose();

    return outcome;
  });
}

describe("AskStoreFactory.create", () => {
  it("create property opens the panel on whatever it is asked about", () => {
    fc.assert(
      fc.property(fc.string(), fc.string(), (question, shownAs) => {
        const opened = withStore((store) => {
          store.askAbout({ question, shownAs });

          return { isOpen: store.isOpen(), pending: store.pendingAsk() };
        });

        expect(opened.isOpen).toBe(true);
        expect(opened.pending).toEqual({ question, shownAs });
      }),
    );
  });

  it("create property leaves the panel open only after an odd toggle count", () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 8 }), (toggles) => {
        const isOpen = withStore((store) => {
          for (let count = 0; count < toggles; count += 1) store.toggle();

          return store.isOpen();
        });

        expect(isOpen).toBe(toggles % 2 === 1);
      }),
    );
  });

  it("create property forgets the pending ask once it was sent", () => {
    fc.assert(
      fc.property(fc.string(), (question) => {
        const pending = withStore((store) => {
          store.askAbout({ question, shownAs: question });
          store.questionSent();

          return store.pendingAsk();
        });

        expect(pending).toBeNull();
      }),
    );
  });

  it("starts closed with nothing pending", () => {
    const started = withStore((store) => ({
      isOpen: store.isOpen(),
      pending: store.pendingAsk(),
    }));

    expect(started).toEqual({ isOpen: false, pending: null });
  });

  it("closes the panel on request", () => {
    const isOpen = withStore((store) => {
      store.toggle();
      store.close();

      return store.isOpen();
    });

    expect(isOpen).toBe(false);
  });
});
