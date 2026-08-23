import type { ExtractedSource, ImportRequest } from "./ImportDialog";
import type {
  SourceExtraction,
  SourceKindHandler,
} from "./source-kind-handler-types";

type SourceBuilder = Pick<SourceKindHandler, "source">;

export async function extractedSource(
  this: SourceBuilder,
  request: ImportRequest,
  extraction: SourceExtraction,
): Promise<ExtractedSource> {
  const source = await this.source(
    request,
    extraction.uploadIntoFolder,
  );

  if (source === null) return { text: "", isNoteAlreadyMade: false };

  return {
    text: await extraction.extractText(source),
    isNoteAlreadyMade: false,
  };
}
