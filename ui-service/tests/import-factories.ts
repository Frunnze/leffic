import fc from "fast-check";
import {
  ImportOptions,
  type SourceKind,
} from "../src/features/folder/import/import-options";
import type { ImportRequest } from "../src/features/folder/import/ImportDialog";

export const sourceKind: fc.Arbitrary<SourceKind> = fc.constantFrom(
  "file",
  "link",
  "text",
  "topic",
);

export function importRequest(
  overrides: Partial<ImportRequest> = {},
): ImportRequest {
  return {
    kind: "text",
    file: null,
    link: "",
    text: "",
    topic: "",
    firstPage: null,
    lastPage: null,
    flashcards: ImportOptions.emptyChoice(),
    test: ImportOptions.emptyChoice(),
    note: ImportOptions.emptyChoice(),
    ...overrides,
  };
}

export function pdfFile(name = "notes.pdf"): File {
  return new File(["%PDF-1.4"], name, { type: "application/pdf" });
}
