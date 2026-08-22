import { describe, expect, it } from "vitest";
import { createRoot } from "solid-js";
import fc from "fast-check";
import {
  ToastStoreFactory,
  type Toast,
  type ToastStore,
} from "../src/shared/notifications/toast-store";

const TONE = fc.constantFrom<Toast["tone"]>("progress", "success", "failure");

function withStore<T>(use: (store: ToastStore) => T): T {
  return createRoot((dispose) => {
    const outcome = use(ToastStoreFactory.create());
    dispose();

    return outcome;
  });
}

describe("ToastStoreFactory.create", () => {
  it("create property shows every toast that was raised, in order", () => {
    fc.assert(
      fc.property(
        fc.array(fc.record({ tone: TONE, title: fc.string() })),
        (raised) => {
          const titles = withStore((store) => {
            for (const toast of raised) store.show(toast);

            return store.toasts().map((toast) => toast.title);
          });

          expect(titles).toEqual(raised.map((toast) => toast.title));
        },
      ),
    );
  });

  it("create property gives every toast an id of its own", () => {
    fc.assert(
      fc.property(
        fc.array(fc.record({ tone: TONE, title: fc.string() }), {
          minLength: 2,
        }),
        (raised) => {
          const ids = withStore((store) =>
            raised.map((toast) => store.show(toast)),
          );

          expect(new Set(ids).size).toBe(ids.length);
        },
      ),
    );
  });

  it("create property dismisses exactly the toast it was told to", () => {
    fc.assert(
      fc.property(TONE, fc.string(), (tone, title) => {
        const remaining = withStore((store) => {
          const kept = store.show({ tone, title });
          const dropped = store.show({ tone, title });
          store.dismiss(dropped);

          return store.toasts().map((toast) => toast.id === kept);
        });

        expect(remaining).toEqual([true]);
      }),
    );
  });

  it("starts with nothing on screen", () => {
    expect(withStore((store) => store.toasts())).toEqual([]);
  });

  it("ignores a dismissal for a toast that is already gone", () => {
    const remaining = withStore((store) => {
      store.show({ tone: "success", title: "kept" });
      store.dismiss("toast-does-not-exist");

      return store.toasts();
    });

    expect(remaining).toHaveLength(1);
  });
});
