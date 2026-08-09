import { HttpClient } from "../../shared/api/http";
import { Json } from "../../shared/api/json";
import type { DueBreakdown } from "../../shared/models/units";

type DuePair = { readonly due: number; readonly done: number };

const NOTHING_DUE: DuePair = { due: 0, done: 0 };

export class StatsApi {
  static async dueBreakdown(folderId: string): Promise<DueBreakdown> {
    const [flashcards, testItems, notes] = await Promise.all([
      StatsApi.flashcards(folderId),
      StatsApi.testItems(folderId),
      StatsApi.notes(folderId),
    ]);

    const doneToday = flashcards.done + testItems.done + notes.done;
    const dueToday = flashcards.due + testItems.due + notes.due;

    return {
      flashcardsDue: flashcards.due,
      testItemsDue: testItems.due,
      notesDue: notes.due,
      doneToday,
      totalToday: doneToday + dueToday,
    };
  }

  private static async flashcards(folderId: string): Promise<DuePair> {
    return StatsApi.readPair(
      `/api/content/flashcards-stats?folder_id=${folderId}`,
      "due",
      "done",
    );
  }

  private static async notes(folderId: string): Promise<DuePair> {
    return StatsApi.readPair(
      `/api/content/notes-stats?folder_id=${folderId}`,
      "due",
      "read",
    );
  }

  private static async testItems(folderId: string): Promise<DuePair> {
    const stats = await StatsApi.readObject(
      `/api/content/test-items-stats?folder_id=${folderId}`,
    );

    if (stats === null) return NOTHING_DUE;

    const total = Json.numberOr(stats.total, 0);
    const correct = Json.numberOr(stats.correct, 0);

    return { due: Math.max(0, total - correct), done: correct };
  }

  private static async readPair(
    endpoint: string,
    dueKey: string,
    doneKey: string,
  ): Promise<DuePair> {
    const stats = await StatsApi.readObject(endpoint);

    if (stats === null) return NOTHING_DUE;

    return {
      due: Json.numberOr(stats[dueKey], 0),
      done: Json.numberOr(stats[doneKey], 0),
    };
  }

  private static async readObject(
    endpoint: string,
  ): Promise<Readonly<Record<string, unknown>> | null> {
    const response = await HttpClient.send({ endpoint });

    if (!response.ok) return null;

    const payload: unknown = await response.json();

    return Json.object(payload, endpoint);
  }
}
