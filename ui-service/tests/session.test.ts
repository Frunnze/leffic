import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { Session } from "../src/shared/api/session";
import { emptyResponse, jsonResponse, stubFetch } from "./support";

function trackNavigation(): { href: string } {
  const location = { href: "/start" };
  Object.defineProperty(window, "location", {
    value: location,
    writable: true,
    configurable: true,
  });

  return location;
}

beforeEach(() => {
  Session.store(null);
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

describe("Session.store and Session.currentToken", () => {
  it("store property hands back whatever token was last stored", () => {
    fc.assert(
      fc.property(fc.string(), (token) => {
        Session.store(token);

        expect(Session.currentToken()).toBe(token);
      }),
    );
  });

  it("currentToken property reads back the stored token unchanged", () => {
    fc.assert(
      fc.property(fc.string(), (token) => {
        Session.store(token);
        Session.store(null);
        Session.store(token);

        expect(Session.currentToken()).toBe(token);
      }),
    );
  });

  it("starts with no token at all", () => {
    expect(Session.currentToken()).toBeNull();
  });
});

describe("Session.refresh", () => {
  it("refresh property stores the token the gateway returned", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string({ minLength: 1 }), async (token) => {
        stubFetch(jsonResponse({ access_token: token }));

        await expect(Session.refresh()).resolves.toBe(token);
        expect(Session.currentToken()).toBe(token);
      }),
    );
  });

  it("forgets the token and leaves for the login page on a 401", async () => {
    const location = trackNavigation();
    Session.store("stale");
    stubFetch(emptyResponse(401));

    await expect(Session.refresh()).resolves.toBeNull();

    expect(Session.currentToken()).toBeNull();
    expect(location.href).toBe("/login");
  });

  it("gives up quietly on any other failure", async () => {
    stubFetch(emptyResponse(500));

    await expect(Session.refresh()).resolves.toBeNull();
  });

  it("stores null when the payload carries no token", async () => {
    stubFetch(jsonResponse({}));

    await expect(Session.refresh()).resolves.toBeNull();
  });

  it("takes the gateway origin the build was given", async () => {
    vi.stubEnv("VITE_GATEWAY_URL", "https://api.example.test");
    vi.resetModules();

    const configured = await import("../src/shared/api/session");

    expect(configured.Session.baseUrl).toBe("https://api.example.test");
  });

  it("falls back to the local gateway when the build named none", () => {
    expect(Session.baseUrl).toBe("http://localhost:8888");
  });

  it("asks the gateway with the refresh cookie", async () => {
    const fetching = stubFetch(jsonResponse({ access_token: "fresh" }));

    await Session.refresh();

    expect(fetching).toHaveBeenCalledWith(
      `${Session.baseUrl}/api/user/refresh-token`,
      { method: "POST", credentials: "include" },
    );
  });
});
