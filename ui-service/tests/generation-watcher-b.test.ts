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
  it("opens no timer for a kind with no jobs", async () => {
    const onOutcome = vi.fn();

    GenerationWatcher.watch(NO_TASKS, onOutcome);

    expect(vi.getTimerCount()).toBe(0);
  });
});

describe("GenerationWatcher.poll", () => {
  it("poll property keeps asking until the job stops being pending", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 4 }), async (rounds) => {
        reportProgress("PENDING");
        const asking = vi.mocked(GenerationApi.progress);
        asking.mockClear();
        const stop = GenerationWatcher.watch(
          { ...NO_TASKS, noteTaskId: "n1" },
          vi.fn(),
        );

        await vi.advanceTimersByTimeAsync(2000 * rounds);
        stop();

        expect(asking).toHaveBeenCalledTimes(rounds);
      }),
    );
  });
});

describe("GenerationWatcher.checkOnce", () => {
  it("checkOnce property stops the timer as soon as the job settles", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom("SUCCESS", "FAILURE" as const),
        async (status) => {
          reportProgress(status);
          const onOutcome = vi.fn();

          GenerationWatcher.watch({ ...NO_TASKS, noteTaskId: "n1" }, onOutcome);
          await vi.advanceTimersByTimeAsync(2000);

          expect(vi.getTimerCount()).toBe(0);
          expect(onOutcome).toHaveBeenCalledWith(
            expect.objectContaining({ succeeded: status === "SUCCESS" }),
          );
        },
      ),
    );
  });
});
