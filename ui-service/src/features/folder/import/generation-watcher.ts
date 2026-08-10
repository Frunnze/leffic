import { GenerationApi, type GeneratedKind } from "./generation-api";
import type { GenerationTaskIds } from "./generation-models";
import type { Unit } from "../../../shared/models/units";

const POLL_INTERVAL_MS = 2000;

export type GenerationOutcome = {
  readonly kind: GeneratedKind;
  readonly succeeded: boolean;
  readonly unit: Unit | null;
};

export class GenerationWatcher {
  static awaitOne(
    kind: GeneratedKind,
    taskId: string | null,
  ): Promise<GenerationOutcome> {
    return new Promise((resolve) => {
      if (taskId === null) {
        resolve({ kind, succeeded: false, unit: null });
        return;
      }

      GenerationWatcher.poll(kind, taskId, resolve);
    });
  }

  static watch(
    tasks: GenerationTaskIds,
    onOutcome: (outcome: GenerationOutcome) => void,
  ): () => void {
    const stops = [
      GenerationWatcher.poll("flashcards", tasks.flashcardsTaskId, onOutcome),
      GenerationWatcher.poll("note", tasks.noteTaskId, onOutcome),
      GenerationWatcher.poll("test", tasks.testTaskId, onOutcome),
    ];

    return () => stops.forEach((stop) => stop());
  }

  private static poll(
    kind: GeneratedKind,
    taskId: string | null,
    onOutcome: (outcome: GenerationOutcome) => void,
  ): () => void {
    if (taskId === null) return () => undefined;

    const timer = window.setInterval(() => {
      void GenerationWatcher.checkOnce(kind, taskId, timer, onOutcome);
    }, POLL_INTERVAL_MS);

    return () => window.clearInterval(timer);
  }

  private static async checkOnce(
    kind: GeneratedKind,
    taskId: string,
    timer: number,
    onOutcome: (outcome: GenerationOutcome) => void,
  ): Promise<void> {
    const progress = await GenerationApi.progress(kind, taskId).catch(() => null);

    if (progress === null) {
      window.clearInterval(timer);
      onOutcome({ kind, succeeded: false, unit: null });
      return;
    }

    if (progress.status === "PENDING") return;

    window.clearInterval(timer);
    onOutcome({
      kind,
      succeeded: progress.status === "SUCCESS",
      unit: progress.unit,
    });
  }
}
