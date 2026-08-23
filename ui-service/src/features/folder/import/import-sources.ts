import type { GenerationWish } from "./generation-api";
import type { ImportRequest } from "./ImportDialog";
import { ImportOptions } from "./import-options";
import type { GenerationOrigin, GenerationSource } from "./generation-models";
import {
  SourceKindHandlers,
} from "./source-kind-handlers";
import type { UploadIntoFolder } from "./source-kind-handler-types";

export const ImportSources = {
  originOf(request: ImportRequest): GenerationOrigin {
    return SourceKindHandlers.of(request.kind).origin(request);
  },

  labelFor(request: ImportRequest): string {
    return SourceKindHandlers.of(request.kind).label(request);
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
    return SourceKindHandlers.of(request.kind).source(
      request,
      uploadIntoFolder,
    );
  },
};
