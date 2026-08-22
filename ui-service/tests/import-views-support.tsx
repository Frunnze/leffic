import { vi, type Mock } from "vitest";
import { type SourceKind } from "../src/features/folder/import/import-options";

export const NO_SOURCE_PROPS = {
  kind: "file" as const,
  chosenFile: null,
  link: "",
  text: "",
  topic: "",
  firstPage: "",
  lastPage: "",
};

type SourceHandlers = {
  onFirstPageChange: Mock<(page: string) => void>;
  onLastPageChange: Mock<(page: string) => void>;
  onKindChange: Mock<(kind: SourceKind) => void>;
  onFileChosen: Mock<(file: File) => void>;
  onLinkChange: Mock<(link: string) => void>;
  onTextChange: Mock<(text: string) => void>;
  onTopicChange: Mock<(topic: string) => void>;
};

export function sourceHandlers(): SourceHandlers {
  return {
    onFirstPageChange: vi.fn(),
    onLastPageChange: vi.fn(),
    onKindChange: vi.fn(),
    onFileChosen: vi.fn(),
    onLinkChange: vi.fn(),
    onTextChange: vi.fn(),
    onTopicChange: vi.fn(),
  };
}
