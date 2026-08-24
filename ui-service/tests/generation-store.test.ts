import { afterEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import {
  GenerationApi,
  type GeneratedKind,
} from "../src/features/folder/import/generation-api";
import { GenerationStoreFactory } from "../src/features/folder/import/generation-store";
import { GenerationWatcher } from "../src/features/folder/import/generation-watcher";
import type { GenerationOutcome } from "../src/features/folder/import/generation-tally";
import type { ToastStore } from "../src/shared/notifications/toast-store";

const EMPTY_TASKS = {
  flashcardsTaskIds: [],
  noteTaskId: null,
  testTaskIds: [],
} as const;

afterEach(() => {
  vi.restoreAllMocks();
});

describe("GenerationStoreFactory", () => {
  it("announcementFor property describes every generated outcome", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom<GeneratedKind>("flashcards", "note", "test"),
        fc.boolean(),
        async (kind, succeeded) => {
          const shown: Parameters<ToastStore["show"]>[0][] = [];
          const toasts: ToastStore = {
            toasts: () => [],
            show: (toast) => {
              shown.push(toast);
              return "progress";
            },
            dismiss: vi.fn(),
          };
          let report: ((outcome: GenerationOutcome) => void) | undefined;

          vi.spyOn(GenerationApi, "start").mockResolvedValue(EMPTY_TASKS);
          vi.spyOn(GenerationWatcher, "watch").mockImplementation(
            (_tasks, onOutcome) => {
              report = onOutcome;
              return vi.fn();
            },
          );

          const store = GenerationStoreFactory.create(toasts);
          expect(store.completionsIn("folder")).toBe(0);

          await store.start({
            source: { kind: "topic", topic: "Neurons" },
            origin: { kind: "topic", reference: "Neurons" },
            folderId: "folder",
            sourceLabel: "Neurons",
            wanted: {
              flashcardTypes: [],
              flashcardAmount: null,
              testTypes: [],
              testAmount: undefined,
              note: true,
            },
          });
          report?.({ kind, succeeded, units: [] });

          expect(shown[1]).toEqual(
            succeeded
              ? {
                  tone: "success",
                  title: `${GenerationApi.labelFor(kind)} ready`,
                }
              : {
                  tone: "failure",
                  title: `Couldn't generate the ${kind}`,
                  detail: "The source could not be processed. Try again.",
                },
          );
          expect(store.completionsIn("folder")).toBe(1);
        },
      ),
    );
  });
});
