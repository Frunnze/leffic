import { HttpClient } from "../../../shared/api/http";
import { Json, type JsonObject } from "../../../shared/api/json";
import type {
  GenerationSource,
  GenerationTaskIds,
  TaskStatus,
  UploadedFile,
} from "./generation-models";
import type { Unit } from "../../../shared/models/units";
import { UnitsApi } from "../units-api";

const STATUS_ENDPOINTS = {
  flashcards: "/api/files/flashcards-status/",
  note: "/api/files/note-task-status/",
  test: "/api/files/test-task-status/",
} as const;

export type GeneratedKind = keyof typeof STATUS_ENDPOINTS;

export type TaskProgress = {
  readonly status: TaskStatus;
  readonly unit: Unit | null;
};

export class GenerationApi {
  static async uploadFile(file: File, folderId: string): Promise<readonly UploadedFile[]> {
    const form = new FormData();
    form.append("files", file);
    form.append("folder_id", folderId);

    const payload = await HttpClient.json({
      endpoint: "/api/files/upload-files",
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

  static async start(
    source: GenerationSource,
    folderId: string,
  ): Promise<GenerationTaskIds> {
    const payload = await HttpClient.json({
      endpoint: "/api/files/generate-study-units",
      method: "POST",
      body: {
        note: {},
        test: {},
        flashcards: {},
        folder_id: folderId,
        ...GenerationApi.sourceBody(source),
      },
    });
    const raw = Json.object(payload, "generation");

    return {
      flashcardsTaskId: Json.stringOrNull(raw.task_id),
      noteTaskId: Json.stringOrNull(raw.note_task_id),
      testTaskId: Json.stringOrNull(raw.test_task_id),
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

  private static sourceBody(source: GenerationSource): Readonly<Record<string, unknown>> {
    if (source.kind === "link") return { link_metadata: source.url };
    if (source.kind === "topic") return { topic_metadata: source.topic };

    return {
      file_metadata: [{ file_id: source.fileId, extension: source.extension }],
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
