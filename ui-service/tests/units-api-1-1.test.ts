import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { UnitsApi } from "../src/features/folder/units-api";
import { UNIT_TYPES } from "../src/features/folder/unit-models";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";
import { unitType } from "./unit-factories";
import { storedUnit } from "./units-api-support";

describe("UnitsApi.folderContent", () => {
  it("folderContent property asks for exactly the folder it was given", async () => {
    await fc.assert(
      fc.asyncProperty(fc.uuid(), async (folderId) => {
        const fetching = stubFetch(jsonResponse({ content: [] }));

        await UnitsApi.folderContent(folderId);

        expect(requestedUrl(fetching)).toContain(
          `folder_id=${encodeURIComponent(folderId)}`,
        );
      }),
    );
  });

  it("folderContent property lists the newest unit first", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(fc.integer({ min: 0, max: 300 }), { minLength: 1 }),
        async (offsets) => {
          const stored = offsets.map((offset, index) =>
            storedUnit({
              id: String(index),
              created_at: new Date(offset * 86_400_000).toISOString(),
            }),
          );
          stubFetch(jsonResponse({ content: stored }));

          const folder = await UnitsApi.folderContent("home");
          const times = folder.units.map((entry) =>
            new Date(entry.createdAt).getTime(),
          );

          expect(times).toEqual([...times].sort((left, right) => right - left));
        },
      ),
    );
  });

  it("names the parent folder Home when the service names none", async () => {
    stubFetch(jsonResponse({ content: [] }));

    await expect(UnitsApi.folderContent("home")).resolves.toEqual({
      parentFolderName: "Home",
      units: [],
    });
  });

  it("carries the parent folder name the service gave", async () => {
    stubFetch(jsonResponse({ content: [], parent_folder_name: "Biology" }));

    await expect(UnitsApi.folderContent("x")).resolves.toMatchObject({
      parentFolderName: "Biology",
    });
  });
});

describe("UnitsApi.toUnit and UnitsApi.toUnitType", () => {
  it("toUnit property keeps every unit type the app knows", () => {
    fc.assert(
      fc.property(unitType, (type) => {
        expect(UnitsApi.toUnit(storedUnit({ type })).type).toBe(type);
      }),
    );
  });

  it("toUnitType property refuses a type the app does not know", () => {
    fc.assert(
      fc.property(
        fc
          .string({ minLength: 1 })
          .filter((name) => !UNIT_TYPES.includes(name as never)),
        (type) => {
          expect(() => UnitsApi.toUnit(storedUnit({ type }))).toThrow(
            `Unknown unit type "${type}"`,
          );
        },
      ),
    );
  });

  it("fills in what a sparse row leaves out", () => {
    expect(UnitsApi.toUnit({ id: 7, type: "file" })).toEqual({
      id: "7",
      name: "Untitled",
      type: "file",
      createdAt: "",
      extension: null,
      dueCount: null,
      meta: null,
    });
  });

  it("reads every optional field a full row carries", () => {
    const read = UnitsApi.toUnit(
      storedUnit({
        type: "file",
        extension: "pdf",
        due_count: 3,
        meta: "3 pages",
      }),
    );

    expect(read).toMatchObject({
      extension: "pdf",
      dueCount: 3,
      meta: "3 pages",
    });
  });
});

describe("UnitsApi.sortByNewest", () => {
  it("sortByNewest property keeps every unit it was given", () => {
    fc.assert(
      fc.property(fc.array(fc.integer({ min: 0, max: 500 })), (offsets) => {
        const units = offsets.map((offset, index) =>
          UnitsApi.toUnit(
            storedUnit({
              id: String(index),
              created_at: new Date(offset * 3_600_000).toISOString(),
            }),
          ),
        );

        expect(UnitsApi.sortByNewest(units)).toHaveLength(units.length);
      }),
    );
  });
});

describe("UnitsApi.createFolder", () => {
  it("createFolder property sends the name and the parent it was given", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string({ minLength: 1 }),
        fc.uuid(),
        async (name, parentFolderId) => {
          const fetching = stubFetch(jsonResponse({ folder_id: "new" }));

          await UnitsApi.createFolder(name, parentFolderId);

          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({
              folder_name: name,
              parent_folder_id: parentFolderId,
            }),
          );
        },
      ),
    );
  });

  it("keeps the name it asked for when the service echoes none", async () => {
    stubFetch(jsonResponse({ folder_id: 12 }));

    const created = await UnitsApi.createFolder("Chemistry", "home");

    expect(created).toMatchObject({
      id: "12",
      name: "Chemistry",
      type: "folder",
      dueCount: null,
    });
    expect(created.createdAt).not.toBe("");
  });

  it("takes the name and moment the service reported", async () => {
    stubFetch(
      jsonResponse({
        folder_id: "9",
        folder_name: "Physics",
        created_at: "2024-05-05T00:00:00.000Z",
      }),
    );

    await expect(
      UnitsApi.createFolder("ignored", "home"),
    ).resolves.toMatchObject({
      name: "Physics",
      createdAt: "2024-05-05T00:00:00.000Z",
    });
  });
});
