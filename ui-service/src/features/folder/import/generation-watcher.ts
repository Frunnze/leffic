import { GenerationApi, type GeneratedKind } from "./generation-api";
import { GenerationTally, type GenerationOutcome } from "./generation-tally";
import type { GenerationTaskIds } from "./generation-models";

const POLL_INTERVAL_MS = 2000;

export class GenerationWatcher {
  static awaitOne(
    kind: GeneratedKind,
    taskId: string | null,
  ): Promise<GenerationOutcome> {
    return new Promise((resolve) => {
      if (taskId === null) {
        resolve({ kind, succeeded: false, units: [] });
        return;
      }

      GenerationWatcher.poll(kind, taskId, resolve);
    });
  }

  static watch(
    tasks: GenerationTaskIds,
    onOutcome: (outcome: GenerationOutcome) => void,
  ): () => void {
    const noteIds = tasks.noteTaskId === null ? [] : [tasks.noteTaskId];
    const stops = [
      ...GenerationWatcher.pollEvery(
        "flashcards",
        tasks.flashcardsTaskIds,
        onOutcome,
      ),
      ...GenerationWatcher.pollEvery("note", noteIds, onOutcome),
      ...GenerationWatcher.pollEvery("test", tasks.testTaskIds, onOutcome),
    ];

    return () => { stops.forEach((stop) => { stop(); }); };
  }

  private static pollEvery(
    kind: GeneratedKind,
    taskIds: readonly string[],
    onOutcome: (outcome: GenerationOutcome) => void,
  ): readonly (() => void)[] {
    if (taskIds.length === 0) return [];

    const tally = new GenerationTally(kind, taskIds.length, onOutcome);

    return taskIds.map((taskId) =>
      GenerationWatcher.poll(kind, taskId, (outcome) => { tally.record(outcome); }),
    );
  }

  private static poll(
    kind: GeneratedKind,
    taskId: string,
    onOutcome: (outcome: GenerationOutcome) => void,
  ): () => void {
    const timer = window.setInterval(() => {
      void GenerationWatcher.checkOnce(kind, taskId, timer, onOutcome);
    }, POLL_INTERVAL_MS);

    return () => { window.clearInterval(timer); };
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
      onOutcome({ kind, succeeded: false, units: [] });
      return;
    }

    if (progress.status === "PENDING") return;

    window.clearInterval(timer);
    onOutcome({
      kind,
      succeeded: progress.status === "SUCCESS",
      units: progress.unit === null ? [] : [progress.unit],
    });
  }
}
