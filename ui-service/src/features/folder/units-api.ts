import { HttpClient } from "../../shared/api/http";
import { Json, type JsonObject } from "../../shared/api/json";
import {
  UNIT_TYPES,
  type FolderContent,
  type Unit,
  type UnitType,
} from "./unit-models";

const DELETE_ENDPOINTS: Readonly<Record<UnitType, string>> = {
  folder: "/api/content/delete-folder/?folder_id=",
  flashcard_deck: "/api/content/delete-deck/?deck_id=",
  test: "/api/content/delete-test/?test_id=",
  note: "/api/content/delete-note/?note_id=",
  file: "/api/content/delete-file/?file_id=",
};

export class UnitsApi {
  static async folderContent(folderId: string): Promise<FolderContent> {
    const query = new URLSearchParams({ folder_id: folderId }).toString();
    const payload = await HttpClient.json({
      endpoint: `/api/content/access-folder/?${query}`,
    });
    const root = Json.object(payload, "folder");
    const rawUnits = Json.array(root.content, "folder.content");

    return {
      parentFolderName: Json.stringOr(root.parent_folder_name, "Home"),
      units: UnitsApi.sortByNewest(
        rawUnits.map((entry, index) =>
          UnitsApi.toUnit(Json.object(entry, `folder.content[${index}]`)),
        ),
      ),
    };
  }

  static async createFolder(name: string, parentFolderId: string): Promise<Unit> {
    const payload = await HttpClient.json({
      endpoint: "/api/content/create-folder",
      method: "POST",
      body: { folder_name: name, parent_folder_id: parentFolderId },
    });
    const created = Json.object(payload, "createdFolder");

    return {
      id: Json.identifier(created.folder_id, "createdFolder.folder_id"),
      name: Json.stringOr(created.folder_name, name),
      type: "folder",
      createdAt: Json.stringOr(created.created_at, new Date().toISOString()),
      extension: null,
      dueCount: null,
      meta: null,
    };
  }

  static async remove(unitId: string, unitType: UnitType): Promise<void> {
    await HttpClient.send({
      endpoint: `${DELETE_ENDPOINTS[unitType]}${unitId}`,
      method: "DELETE",
    });
  }

  static async rename(
    unitId: string,
    unitType: UnitType,
    name: string,
  ): Promise<void> {
    await HttpClient.json({
      endpoint: "/api/content/rename-unit",
      method: "PATCH",
      body: { unit_id: unitId, unit_type: unitType, name },
    });
  }

  static async move(
    unitId: string,
    unitType: UnitType,
    folderId: string,
  ): Promise<void> {
    await HttpClient.json({
      endpoint: "/api/content/move-unit",
      method: "PATCH",
      body: { unit_id: unitId, unit_type: unitType, folder_id: folderId },
    });
  }

  static toUnit(raw: JsonObject): Unit {
    return {
      id: Json.identifier(raw.id, "unit.id"),
      name: Json.stringOr(raw.name, "Untitled"),
      type: UnitsApi.toUnitType(raw.type),
      createdAt: Json.stringOr(raw.created_at, ""),
      extension: Json.optionalString(raw.extension),
      dueCount: Json.optionalNumber(raw.due_count),
      meta: Json.optionalString(raw.meta),
    };
  }

  static sortByNewest(units: readonly Unit[]): readonly Unit[] {
    return [...units].sort(
      (left, right) =>
        new Date(right.createdAt).getTime() - new Date(left.createdAt).getTime(),
    );
  }

  private static toUnitType(value: unknown): UnitType {
    const name = Json.string(value, "unit.type");
    const known = UNIT_TYPES.find((candidate) => candidate === name);

    if (known === undefined) {
      throw new Error(`Unknown unit type "${name}"`);
    }

    return known;
  }
}
