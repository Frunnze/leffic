import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { HttpClient } from "../src/shared/api/http";
import { blobResponse, emptyResponse, stubFetch } from "./support";
import { ENDPOINT } from "./http-support";

describe("HttpClient.blob", () => {
  it("blob property hands back the bytes the gateway sent", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), async (body) => {
        stubFetch(blobResponse(body));

        const downloaded = await HttpClient.blob({ endpoint: ENDPOINT });

        await expect(downloaded.text()).resolves.toBe(body);
      }),
    );
  });

  it("refuses to hand back bytes the gateway would not send", async () => {
    stubFetch(emptyResponse(500));

    await expect(HttpClient.blob({ endpoint: ENDPOINT })).rejects.toThrow(
      "failed with status 500",
    );
  });
});
