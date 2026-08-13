export type SourceKind = "file" | "link" | "text" | "topic";

export type CardTypeOption = {
  readonly id: string;
  readonly label: string;
  readonly isSupported: boolean;
};

export type UnitChoice = {
  readonly isChosen: boolean;
  readonly counts: Readonly<Record<string, number | null>>;
  readonly chosenTypes: readonly string[];
};

export const PAGED_EXTENSIONS: readonly string[] = [
  "pdf",
  "doc",
  "docx",
  "odt",
  "rtf",
  "ppt",
  "pptx",
  "odp",
];

export const SOURCE_KINDS: readonly { kind: SourceKind; label: string }[] = [
  { kind: "file", label: "File" },
  { kind: "link", label: "Link" },
  { kind: "text", label: "Text" },
  { kind: "topic", label: "Topic" },
];

export const FLASHCARD_TYPES: readonly CardTypeOption[] = [
  { id: "basic", label: "Basic", isSupported: true },
  { id: "cloze", label: "Fill in the blank", isSupported: true },
  { id: "list", label: "List", isSupported: true },
  { id: "feynman", label: "Feynman", isSupported: true },
];

export const TEST_TYPES: readonly CardTypeOption[] = [
  { id: "multiple_choice", label: "Multiple choice", isSupported: true },
  { id: "true_or_false", label: "True or false", isSupported: true },
  { id: "short_answer", label: "Short answer", isSupported: true },
];

export class ImportOptions {
  static emptyChoice(): UnitChoice {
    return { isChosen: false, counts: {}, chosenTypes: [] };
  }

  static startingChoice(typeId: string): UnitChoice {
    return { isChosen: true, counts: {}, chosenTypes: [typeId] };
  }

  static withType(choice: UnitChoice, typeId: string): UnitChoice {
    const chosenTypes = choice.chosenTypes.includes(typeId)
      ? choice.chosenTypes.filter((entry) => entry !== typeId)
      : [...choice.chosenTypes, typeId];

    return { ...choice, chosenTypes };
  }

  static withCount(
    choice: UnitChoice,
    typeId: string,
    count: number | null,
  ): UnitChoice {
    return { ...choice, counts: { ...choice.counts, [typeId]: count } };
  }

  static totalCount(choice: UnitChoice): number | null {
    const counted = choice.chosenTypes
      .map((typeId) => choice.counts[typeId] ?? null)
      .filter((count): count is number => count !== null);

    if (counted.length === 0) return null;

    return counted.reduce((total, count) => total + count, 0);
  }
}
