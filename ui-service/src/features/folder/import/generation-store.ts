import { createSignal } from "solid-js";
import { GenerationApi, type GenerationWish } from "./generation-api";
import { GenerationWatcher, type GenerationOutcome } from "./generation-watcher";
import type { GenerationOrigin, GenerationSource } from "./generation-models";
import type { Toast, ToastStore } from "../../notifications/toast-store";

const KIND_LABELS = {
  flashcards: "Flashcards",
  note: "Note",
  test: "Test",
} as const;

export type GenerationRequest = {
  readonly source: GenerationSource;
  readonly origin: GenerationOrigin;
  readonly folderId: string;
  readonly sourceLabel: string;
  readonly wanted: GenerationWish;
};

export type GenerationStore = {
  readonly start: (request: GenerationRequest) => Promise<void>;
  readonly completionsIn: (folderId: string) => number;
};

function announcementFor(outcome: GenerationOutcome): Omit<Toast, "id"> {
  if (outcome.succeeded) {
    return { tone: "success", title: `${KIND_LABELS[outcome.kind]} ready` };
  }

  return {
    tone: "failure",
    title: `Couldn't generate the ${outcome.kind}`,
    detail: "The source could not be processed. Try again.",
  };
}

export class GenerationStoreFactory {
  static create(toasts: ToastStore): GenerationStore {
    const [completions, setCompletions] = createSignal<
      Readonly<Record<string, number>>
    >({});

    const recordCompletion = (folderId: string): void => {
      setCompletions((counted) => ({
        ...counted,
        [folderId]: (counted[folderId] ?? 0) + 1,
      }));
    };

    const start = async (request: GenerationRequest): Promise<void> => {
      const progressToast = toasts.show({
        tone: "progress",
        title: `Generating from ${request.sourceLabel}`,
      });
      const tasks = await GenerationApi.start(
        request.source,
        request.origin,
        request.folderId,
        request.wanted,
      );

      GenerationWatcher.watch(tasks, (outcome) => {
        toasts.dismiss(progressToast);
        recordCompletion(request.folderId);
        toasts.show(announcementFor(outcome));
      });
    };

    return {
      start,
      completionsIn: (folderId) => completions()[folderId] ?? 0,
    };
  }
}
