import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { UnitsApi } from "../src/features/folder/units-api";
import { jsonResponse, requestedInit, stubFetch } from "./support";
import { unitType } from "./unit-factories";
import "./units-api-support";

describe("UnitsApi.rename", () => {
  it("rename property sends the whole rename as one patch", async () => {
    await fc.assert(
      fc.asyncProperty(
        unitType,
        fc.uuid(),
        fc.string(),
        async (type, unitId, name) => {
          const fetching = stubFetch(jsonResponse({}));

          await UnitsApi.rename(unitId, type, name);

          expect(requestedInit(fetching).method).toBe("PATCH");
          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({ unit_id: unitId, unit_type: type, name }),
          );
        },
      ),
    );
  });
});

describe("UnitsApi.move", () => {
  it("move property names the destination folder in the patch", async () => {
    await fc.assert(
      fc.asyncProperty(
        unitType,
        fc.uuid(),
        fc.uuid(),
        async (type, unitId, folderId) => {
          const fetching = stubFetch(jsonResponse({}));

          await UnitsApi.move(unitId, type, folderId);

          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({
              unit_id: unitId,
              unit_type: type,
              folder_id: folderId,
            }),
          );
        },
      ),
    );
  });
});
