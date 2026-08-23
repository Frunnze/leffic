import type { ImportRequest } from "./ImportDialog";
import { SourceKindHandlers } from "./source-kind-handlers";

export class ImportRequestReading {
  static chosenPage(typed: string): number | null {
    const page = Number.parseInt(typed, 10);

    return Number.isNaN(page) ? null : page;
  }

  static missingSource(request: ImportRequest): string | null {
    return SourceKindHandlers.of(request.kind).missingSource(request);
  }

  static sourceName(request: ImportRequest): string {
    return SourceKindHandlers.of(request.kind).sourceName(request);
  }

  static nothingChosen(request: ImportRequest): boolean {
    return (
      !request.flashcards.isChosen &&
      !request.test.isChosen &&
      !request.note.isChosen
    );
  }
}
