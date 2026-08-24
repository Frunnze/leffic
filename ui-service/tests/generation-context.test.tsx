import { For, type JSX } from "solid-js";
import { render } from "@solidjs/testing-library";
import { describe, expect, it } from "vitest";
import fc from "fast-check";
import {
  GenerationProvider,
  useGenerations,
} from "../src/features/folder/import/GenerationContext";
import type { GenerationStore } from "../src/features/folder/import/generation-store";
import { ToastProvider } from "../src/shared/notifications/ToastContext";

type GenerationReaderProps = {
  readonly onRead: (store: GenerationStore) => void;
};

function GenerationReader(props: GenerationReaderProps): JSX.Element {
  props.onRead(useGenerations());

  return <span />;
}

describe("useGenerations", () => {
  it("useGenerations property gives every reader the same store", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 5 }), (readerCount) => {
        const stores: GenerationStore[] = [];
        const readers = Array.from({ length: readerCount }, (_, index) => index);
        const { unmount } = render(() => (
          <ToastProvider>
            <GenerationProvider>
              <For each={readers}>
                {() => <GenerationReader onRead={(store) => stores.push(store)} />}
              </For>
            </GenerationProvider>
          </ToastProvider>
        ));

        expect(new Set(stores).size).toBe(1);
        unmount();
      }),
      { numRuns: 5 },
    );
  });

  it("refuses to be read outside a provider", () => {
    expect(() =>
      render(() => <GenerationReader onRead={() => undefined} />),
    ).toThrow("useGenerations must be used inside a GenerationProvider");
  });
});
