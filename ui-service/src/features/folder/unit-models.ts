import type { UnitType } from "./unit-definitions";

export { UNIT_TYPES, type UnitType } from "./unit-definitions";

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
