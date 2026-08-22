import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { HttpClient } from "../src/shared/api/http";
import { emptyResponse, jsonResponse, stubFetch } from "./support";
import { ENDPOINT } from "./http-support";

describe("HttpClient.json", () => {
  it("json property hands back exactly what the gateway sent", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.dictionary(fc.string(), fc.integer()),
        async (payload) => {
          stubFetch(jsonResponse(payload));

          await expect(
            HttpClient.json({ endpoint: ENDPOINT }),
          ).resolves.toEqual(payload);
        },
      ),
    );
  });

  it("names the endpoint and status when the call failed", async () => {
    stubFetch(emptyResponse(404));

    await expect(HttpClient.json({ endpoint: ENDPOINT })).rejects.toThrow(
      `Request to ${ENDPOINT} failed with status 404`,
    );
  });
});
