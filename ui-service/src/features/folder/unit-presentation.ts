import type { IconName } from "../../shared/ui/icons/icon-shapes";
import type { MoveDestination } from "./MoveUnitDialog";
import { UNIT_DEFINITIONS } from "./unit-definitions";
import type { Unit } from "./unit-models";

const HOME_FOLDER_ID = "home";

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
    return UNIT_DEFINITIONS[unit.type].icon;
  }

  static href(unit: Unit): string {
    const extension = unit.type === "file" ? `/${unit.extension ?? ""}` : "";

    return `${UNIT_DEFINITIONS[unit.type].hrefPrefix}/${unit.id}${extension}`;
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
