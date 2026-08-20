import type { GenerationWish } from "./generation-api";
import type { ImportRequest } from "./ImportDialog";
import { ImportOptions } from "./import-options";
import type {
  GenerationOrigin,
  GenerationSource,
  UploadedFile,
} from "./generation-models";

type UploadIntoFolder = (chosen: File) => Promise<readonly UploadedFile[]>;

export const ImportSources = {
  originOf(request: ImportRequest): GenerationOrigin {
    if (request.kind === "file") {
      return { kind: "file", reference: request.file?.name ?? "" };
    }
    if (request.kind === "link") {
      return { kind: "link", reference: request.link };
    }
    if (request.kind === "topic") {
      return { kind: "topic", reference: request.topic };
    }

    return { kind: "text", reference: "" };
  },

  labelFor(request: ImportRequest): string {
    if (request.kind === "file") return request.file?.name ?? "your file";
    if (request.kind === "link") return request.link;
    if (request.kind === "topic") return request.topic;

    return "your text";
  },

  wishFrom(request: ImportRequest): GenerationWish {
    return {
      flashcardTypes: request.flashcards.isChosen
        ? request.flashcards.chosenTypes
        : [],
      flashcardAmount: ImportOptions.totalCount(request.flashcards),
      testTypes: request.test.isChosen ? request.test.chosenTypes : [],
      testAmount: request.test.isChosen
        ? ImportOptions.totalCount(request.test)
        : undefined,
      note: request.note.isChosen,
    };
  },

  async sourceFrom(
    request: ImportRequest,
    uploadIntoFolder: UploadIntoFolder,
  ): Promise<GenerationSource | null> {
    if (request.kind === "link") return { kind: "link", url: request.link };
    if (request.kind === "topic") {
      return { kind: "topic", topic: request.topic };
    }
    if (request.kind === "text") {
      return { kind: "topic", topic: request.text };
    }

    const chosen = request.file;
    if (chosen === null) return null;

    const uploaded = await uploadIntoFolder(chosen);
    const first = uploaded[0];

    if (first === undefined) return null;

    return {
      kind: "file",
      fileId: first.fileId,
      extension: first.extension,
      firstPage: request.firstPage,
      lastPage: request.lastPage,
    };
  },
};
