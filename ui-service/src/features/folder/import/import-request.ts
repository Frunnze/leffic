import type { ImportRequest } from "./ImportDialog";

export class ImportRequestReading {
  static chosenPage(typed: string): number | null {
    const page = Number.parseInt(typed, 10);

    return Number.isNaN(page) ? null : page;
  }

  static missingSource(request: ImportRequest): string | null {
    if (request.kind === "file" && request.file === null) {
      return "Choose a file first.";
    }
    if (request.kind === "link" && request.link.trim().length === 0) {
      return "Paste a link first.";
    }
    if (request.kind === "topic" && request.topic.trim().length === 0) {
      return "Name a topic first.";
    }
    if (request.kind === "text" && request.text.trim().length === 0) {
      return "Paste some text first.";
    }

    return null;
  }

  static sourceName(request: ImportRequest): string {
    if (request.kind === "file") return request.file?.name ?? "";
    if (request.kind === "link") return request.link;
    if (request.kind === "topic") return request.topic;

    return "your text";
  }

  static nothingChosen(request: ImportRequest): boolean {
    return (
      !request.flashcards.isChosen &&
      !request.test.isChosen &&
      !request.note.isChosen
    );
  }
}
