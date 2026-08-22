import { HttpClient } from "../../../shared/api/http";
import { Json, type JsonObject } from "../../../shared/api/json";
import type {
  GenerationOrigin,
  GenerationSource,
  GenerationTaskIds,
  TaskStatus,
  UploadedFile,
} from "./generation-models";
import type { Unit } from "../unit-models";
import { UnitsApi } from "../units-api";

const STATUS_ENDPOINTS = {
  flashcards: "/api/content/flashcards-status/",
  note: "/api/content/note-task-status/",
  test: "/api/content/test-task-status/",
} as const;

export type GeneratedKind = keyof typeof STATUS_ENDPOINTS;

export type GenerationWish = {
  readonly flashcardTypes: readonly string[];
  readonly flashcardAmount: number | null;
  readonly testTypes: readonly string[];
  readonly testAmount: number | null | undefined;
  readonly note: boolean;
};

const DEFAULT_WISH: GenerationWish = {
  flashcardTypes: ["basic"],
  flashcardAmount: null,
  testTypes: ["multiple_choice"],
  testAmount: null,
  note: true,
};

type TaskProgress = {
  readonly status: TaskStatus;
  readonly unit: Unit | null;
};

export class GenerationApi {
  static async uploadFile(file: File, folderId: string): Promise<readonly UploadedFile[]> {
    const form = new FormData();
    form.append("files", file);
    form.append("folder_id", folderId);

    const payload = await HttpClient.json({
      endpoint: "/api/content/upload-files",
      method: "POST",
      body: form,
    });
    const raw = Json.array(
      Json.object(payload, "upload").file_metadata,
      "upload.file_metadata",
    );

    return raw.map((entry, index) =>
      GenerationApi.toUploadedFile(Json.object(entry, `upload.file_metadata[${index}]`)),
    );
  }

  static async extractText(source: GenerationSource): Promise<string> {
    const payload = await HttpClient.json({
      endpoint: "/api/content/extract-text",
      method: "POST",
      body: GenerationApi.sourceBody(source),
    });

    return Json.string(Json.object(payload, "extraction").text, "text");
  }

  static async start(
    source: GenerationSource,
    origin: GenerationOrigin,
    folderId: string,
    wanted: GenerationWish = DEFAULT_WISH,
  ): Promise<GenerationTaskIds> {
    const text = await GenerationApi.sourceText(source);
    const payload = await HttpClient.json({
      endpoint: "/api/content/generate-study-units",
      method: "POST",
      body: {
        ...GenerationApi.wishBody(wanted),
        folder_id: folderId,
        text,
        source_kind: origin.kind,
        source_reference: origin.reference,
      },
    });
    const raw = Json.object(payload, "generation");

    return {
      flashcardsTaskIds: Json.strings(raw.flashcard_task_ids),
      noteTaskId: Json.optionalString(raw.note_task_id),
      testTaskIds: Json.strings(raw.test_task_ids),
    };
  }

  static async progress(kind: GeneratedKind, taskId: string): Promise<TaskProgress> {
    const payload = await HttpClient.json({
      endpoint: `${STATUS_ENDPOINTS[kind]}${taskId}`,
    });
    const raw = Json.object(payload, "taskProgress");
    const status = GenerationApi.toStatus(raw.status);

    return {
      status,
      unit: status === "SUCCESS" ? GenerationApi.toGeneratedUnit(kind, raw) : null,
    };
  }

  private static async sourceText(source: GenerationSource): Promise<string> {
    if (source.kind === "topic") return source.topic;

    return GenerationApi.extractText(source);
  }

  private static wishBody(
    wanted: GenerationWish,
  ): Readonly<Record<string, unknown>> {
    const body: Record<string, unknown> = {};

    if (wanted.note) body.note = {};

    if (wanted.flashcardTypes.length > 0) {
      body.flashcards = {
        types: wanted.flashcardTypes,
        amount: wanted.flashcardAmount,
      };
    }

    if (wanted.testAmount !== undefined) {
      const test: Record<string, unknown> = { types: wanted.testTypes };

      if (wanted.testAmount !== null) test.amount = wanted.testAmount;

      body.test = test;
    }

    return body;
  }

  private static sourceBody(source: GenerationSource): Readonly<Record<string, unknown>> {
    if (source.kind === "link") return { link_metadata: source.url };
    if (source.kind === "topic") return { topic_metadata: source.topic };

    const pages: Record<string, number> = {};

    if (source.firstPage !== null) pages.first = source.firstPage;
    if (source.lastPage !== null) pages.last = source.lastPage;

    const asked = Object.keys(pages).length === 0 ? {} : { pages };

    return {
      file_metadata: [
        { file_id: source.fileId, extension: source.extension, ...asked },
      ],
    };
  }

  private static toGeneratedUnit(kind: GeneratedKind, raw: JsonObject): Unit | null {
    const idField = { flashcards: "flashcard_deck_id", note: "note_id", test: "test_id" }[kind];
    const id = raw[idField];

    if (id === undefined || id === null) return null;

    return UnitsApi.toUnit({ ...raw, id });
  }

  private static toUploadedFile(raw: JsonObject): UploadedFile {
    return {
      fileId: Json.identifier(raw.file_id, "uploadedFile.file_id"),
      name: Json.stringOr(raw.name, "Untitled file"),
      extension: Json.stringOr(raw.extension, ""),
      createdAt: Json.stringOr(raw.created_at, new Date().toISOString()),
    };
  }

  private static toStatus(value: unknown): TaskStatus {
    const name = Json.stringOr(value, "PENDING");

    if (name === "SUCCESS" || name === "FAILURE") return name;

    return "PENDING";
  }
}
