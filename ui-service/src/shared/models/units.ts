export type UnitType = "folder" | "flashcard_deck" | "test" | "note" | "file";

export const UNIT_TYPES: readonly UnitType[] = [
  "folder",
  "flashcard_deck",
  "test",
  "note",
  "file",
];

export type Unit = {
  readonly id: string;
  readonly name: string;
  readonly type: UnitType;
  readonly createdAt: string;
  readonly extension: string | null;
  readonly dueCount: number | null;
  readonly meta: string | null;
};

export type FolderContent = {
  readonly parentFolderName: string;
  readonly units: readonly Unit[];
};

export type DueBreakdown = {
  readonly flashcardsDue: number;
  readonly testItemsDue: number;
  readonly notesDue: number;
  readonly doneToday: number;
  readonly totalToday: number;
};
