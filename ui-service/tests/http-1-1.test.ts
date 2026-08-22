import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { HttpClient, UnauthorizedError } from "../src/shared/api/http";
import { Session } from "../src/shared/api/session";
import {
  emptyResponse,
  jsonResponse,
  requestedInit,
  requestedUrl,
  sentHeaders,
  stubFetch,
} from "./support";
import { ENDPOINT } from "./http-support";

describe("HttpClient.send", () => {
  it("send property always calls the gateway origin plus the endpoint", async () => {
    await fc.assert(
      fc.asyncProperty(fc.webPath(), async (endpoint) => {
        const fetching = stubFetch(emptyResponse(200));

        await HttpClient.send({ endpoint });

        expect(requestedUrl(fetching)).toBe(`${Session.baseUrl}${endpoint}`);
      }),
    );
  });

  it("send property carries the stored token as a bearer header", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string({ minLength: 1 }), async (token) => {
        Session.store(token);
        const fetching = stubFetch(emptyResponse(200));

        await HttpClient.send({ endpoint: ENDPOINT });

        expect(sentHeaders(fetching).Authorization).toBe(`Bearer ${token}`);
      }),
    );
  });

  it("refreshes first when no token is held yet", async () => {
    Session.store(null);
    const fetching = stubFetch(
      jsonResponse({ access_token: "fresh" }),
      emptyResponse(200),
    );

    await HttpClient.send({ endpoint: ENDPOINT });

    expect(sentHeaders(fetching, 1).Authorization).toBe("Bearer fresh");
  });

  it("refuses the call when the refresh brings back nothing", async () => {
    Session.store(null);
    stubFetch(emptyResponse(500));

    await expect(HttpClient.send({ endpoint: ENDPOINT })).rejects.toThrow(
      UnauthorizedError,
    );
  });

  it("retries once with a fresh token after a 401", async () => {
    const fetching = stubFetch(
      emptyResponse(401),
      jsonResponse({ access_token: "second" }),
      emptyResponse(200),
    );

    const response = await HttpClient.send({ endpoint: ENDPOINT });

    expect(response.status).toBe(200);
    expect(sentHeaders(fetching, 2).Authorization).toBe("Bearer second");
  });

  it("gives up when the retry cannot be authorised", async () => {
    stubFetch(emptyResponse(401), emptyResponse(500));

    await expect(HttpClient.send({ endpoint: ENDPOINT })).rejects.toThrow(
      "The session expired and could not be refreshed",
    );
  });

  it("leaves a 401 alone on a request that needs no token", async () => {
    const fetching = stubFetch(emptyResponse(401));

    const response = await HttpClient.send({
      endpoint: ENDPOINT,
      withToken: false,
    });

    expect(response.status).toBe(401);
    expect(sentHeaders(fetching).Authorization).toBeUndefined();
  });

  it("sends no bearer header when nothing was ever stored", async () => {
    Session.store(null);
    const fetching = stubFetch(jsonResponse({}), emptyResponse(200));

    await HttpClient.send({ endpoint: ENDPOINT, withToken: false });

    expect(sentHeaders(fetching).Authorization).toBeUndefined();
  });
});

describe("HttpClient.dispatch", () => {
  it("dispatch property passes the asked-for method straight through", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom("GET", "POST", "PUT", "PATCH", "DELETE"),
        async (method) => {
          const fetching = stubFetch(emptyResponse(200));

          await HttpClient.send({ endpoint: ENDPOINT, method });

          expect(requestedInit(fetching).method).toBe(method);
        },
      ),
    );
  });

  it("defaults to a same-origin GET", async () => {
    const fetching = stubFetch(emptyResponse(200));

    await HttpClient.send({ endpoint: ENDPOINT });

    expect(requestedInit(fetching)).toMatchObject({
      method: "GET",
      credentials: "same-origin",
      body: null,
    });
  });

  it("passes the asked-for credentials mode", async () => {
    const fetching = stubFetch(emptyResponse(200));

    await HttpClient.send({ endpoint: ENDPOINT, credentials: "include" });

    expect(requestedInit(fetching).credentials).toBe("include");
  });
});

describe("HttpClient.encodeBody", () => {
  it("encodeBody property sends an object as json text", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.dictionary(fc.string(), fc.string()),
        async (body) => {
          const fetching = stubFetch(emptyResponse(200));

          await HttpClient.send({ endpoint: ENDPOINT, method: "POST", body });

          expect(requestedInit(fetching).body).toBe(JSON.stringify(body));
          expect(sentHeaders(fetching)["Content-Type"]).toBe(
            "application/json",
          );
        },
      ),
    );
  });

  it("sends form data untouched and without a json header", async () => {
    const body = new FormData();
    body.append("file", new File(["x"], "x.pdf"));
    const fetching = stubFetch(emptyResponse(200));

    await HttpClient.send({ endpoint: ENDPOINT, method: "POST", body });

    expect(requestedInit(fetching).body).toBe(body);
    expect(sentHeaders(fetching)["Content-Type"]).toBeUndefined();
  });

  it("keeps the headers the caller asked for", async () => {
    const fetching = stubFetch(emptyResponse(200));

    await HttpClient.send({
      endpoint: ENDPOINT,
      headers: { Accept: "text/plain" },
    });

    expect(sentHeaders(fetching).Accept).toBe("text/plain");
  });
});
