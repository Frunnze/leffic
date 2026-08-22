import type { IconName } from "../../shared/ui/icons/icon-shapes";
import type { MoveDestination } from "./MoveUnitDialog";
import type { Unit, UnitType } from "./unit-models";

const HOME_FOLDER_ID = "home";

const UNIT_ICONS: Readonly<Record<UnitType, IconName>> = {
  folder: "folder",
  flashcard_deck: "flashcards",
  test: "test",
  note: "note",
  file: "file",
};

export class UnitPresentation {
  static moveDestinations(
    units: readonly Unit[],
    moving: Unit,
  ): readonly MoveDestination[] {
    const folders = units.filter(
      (entry) => entry.type === "folder" && entry.id !== moving.id,
    );

    return [
      { id: HOME_FOLDER_ID, name: "Home" },
      ...folders.map((entry) => ({ id: entry.id, name: entry.name })),
    ];
  }

  static icon(unit: Unit): IconName {
    return UNIT_ICONS[unit.type];
  }

  static href(unit: Unit): string {
    if (unit.type === "folder") return `/folder/${unit.id}`;
    if (unit.type === "file") {
      return `/file/${unit.id}/${unit.extension ?? ""}`;
    }
    if (unit.type === "flashcard_deck") return `/flashcard_deck/${unit.id}`;

    return `/${unit.type}/${unit.id}`;
  }

  static meta(unit: Unit): string | null {
    if (unit.meta !== null) return unit.meta;
    if (unit.type === "file" && unit.extension !== null) {
      return unit.extension.toUpperCase();
    }

    return null;
  }

  static badge(unit: Unit): string | null {
    if (unit.dueCount === null || unit.dueCount <= 0) return null;

    return `${unit.dueCount} due`;
  }

  static countLabel(total: number): string {
    return total === 1 ? "1 item" : `${total} items`;
  }
}
