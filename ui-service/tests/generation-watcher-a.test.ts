import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import {
  GenerationWatcher,
} from "../src/features/folder/import/generation-watcher";
import { GenerationApi } from "../src/features/folder/import/generation-api";
import { unitOf } from "./unit-factories";

const NO_TASKS = {
  flashcardsTaskIds: [],
  noteTaskId: null,
  testTaskIds: [],
};

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});

function reportProgress(status: "PENDING" | "SUCCESS" | "FAILURE"): void {
  vi.spyOn(GenerationApi, "progress").mockResolvedValue({
    status,
    unit: status === "SUCCESS" ? unitOf({ id: "made" }) : null,
  });
}

describe("GenerationWatcher.awaitOne", () => {
  it("awaitOne property gives up at once on a job that was never opened", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom("flashcards", "note", "test" as const),
        async (kind) => {
          await expect(GenerationWatcher.awaitOne(kind, null)).resolves.toEqual(
            {
              kind,
              succeeded: false,
              unit: null,
            },
          );
        },
      ),
    );
  });

  it("resolves once the job succeeds", async () => {
    reportProgress("SUCCESS");
    const awaited = GenerationWatcher.awaitOne("note", "task-1");

    await vi.advanceTimersByTimeAsync(2000);

    await expect(awaited).resolves.toMatchObject({
      kind: "note",
      succeeded: true,
    });
  });
});

describe("GenerationWatcher.watch, pollEvery, poll and checkOnce", () => {
  it("watch property reports one outcome per kind that was asked for", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 3 }), async (jobCount) => {
        reportProgress("SUCCESS");
        const onOutcome = vi.fn();

        GenerationWatcher.watch(
          {
            flashcardsTaskIds: Array.from(
              { length: jobCount },
              (_, i) => `f${i}`,
            ),
            noteTaskId: null,
            testTaskIds: [],
          },
          onOutcome,
        );

        await vi.advanceTimersByTimeAsync(2000);

        expect(onOutcome).toHaveBeenCalledTimes(1);
      }),
    );
  });

  it("watches nothing when no job was opened", async () => {
    const onOutcome = vi.fn();

    GenerationWatcher.watch(NO_TASKS, onOutcome);
    await vi.advanceTimersByTimeAsync(10_000);

    expect(onOutcome).not.toHaveBeenCalled();
  });

  it("watches the note job when there is one", async () => {
    reportProgress("SUCCESS");
    const onOutcome = vi.fn();

    GenerationWatcher.watch({ ...NO_TASKS, noteTaskId: "n1" }, onOutcome);
    await vi.advanceTimersByTimeAsync(2000);

    expect(onOutcome).toHaveBeenCalledWith(
      expect.objectContaining({ kind: "note", succeeded: true }),
    );
  });

  it("watches the test jobs when there are some", async () => {
    reportProgress("FAILURE");
    const onOutcome = vi.fn();

    GenerationWatcher.watch({ ...NO_TASKS, testTaskIds: ["t1"] }, onOutcome);
    await vi.advanceTimersByTimeAsync(2000);

    expect(onOutcome).toHaveBeenCalledWith({
      kind: "test",
      succeeded: false,
      unit: null,
    });
  });

  it("keeps waiting while the job is still pending", async () => {
    reportProgress("PENDING");
    const onOutcome = vi.fn();

    GenerationWatcher.watch({ ...NO_TASKS, noteTaskId: "n1" }, onOutcome);
    await vi.advanceTimersByTimeAsync(6000);

    expect(onOutcome).not.toHaveBeenCalled();
  });

  it("gives up on a job whose status cannot be read", async () => {
    vi.spyOn(GenerationApi, "progress").mockRejectedValue(new Error("gone"));
    const onOutcome = vi.fn();

    GenerationWatcher.watch({ ...NO_TASKS, noteTaskId: "n1" }, onOutcome);
    await vi.advanceTimersByTimeAsync(2000);

    expect(onOutcome).toHaveBeenCalledWith({
      kind: "note",
      succeeded: false,
      unit: null,
    });
  });

  it("stops polling when the watcher is told to stop", async () => {
    reportProgress("PENDING");
    const onOutcome = vi.fn();

    const stop = GenerationWatcher.watch(
      { ...NO_TASKS, noteTaskId: "n1" },
      onOutcome,
    );
    stop();
    reportProgress("SUCCESS");
    await vi.advanceTimersByTimeAsync(10_000);

    expect(onOutcome).not.toHaveBeenCalled();
  });
});

describe("GenerationWatcher.pollEvery", () => {
  it("pollEvery property waits for every job of a kind before reporting", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 3 }), async (jobCount) => {
        reportProgress("SUCCESS");
        const onOutcome = vi.fn();

        GenerationWatcher.watch(
          {
            ...NO_TASKS,
            testTaskIds: Array.from({ length: jobCount }, (_, i) => `t${i}`),
          },
          onOutcome,
        );
        await vi.advanceTimersByTimeAsync(2000);

        expect(onOutcome).toHaveBeenCalledTimes(1);
      }),
    );
  });
});
