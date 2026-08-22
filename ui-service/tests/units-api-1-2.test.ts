import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { UnitsApi } from "../src/features/folder/units-api";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";
import { unitType } from "./unit-factories";
import "./units-api-support";

describe("UnitsApi.remove", () => {
  it("remove property asks the endpoint that belongs to the unit type", async () => {
    await fc.assert(
      fc.asyncProperty(unitType, fc.uuid(), async (type, unitId) => {
        const fetching = stubFetch(jsonResponse({}));

        await UnitsApi.remove(unitId, type);

        expect(requestedUrl(fetching)).toContain(unitId);
        expect(requestedInit(fetching).method).toBe("DELETE");
      }),
    );
  });
});
