import { describe, expect, it } from "vitest";
import {
  declaredMaps,
  mappedValueFor,
  rateLimitSelectorMaps,
} from "./nginx-selector-support";
import {
  AUTHENTICATION_LIMITED_ROUTES,
  AUTHENTICATION_UNLIMITED_ROUTES,
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_LIMITED_ROUTES,
  GENERATION_COST_ZONE_WORD,
  SELECTOR_MAP_COUNT,
  UNCOUNTED_ROUTES,
  selectorOf,
} from "./rate-limit-support";

const REQUEST_URI_VARIABLE = "$request_uri";
const NORMALISED_URI_VARIABLE = "$uri";

function authenticationValueFor(requestUri: string): string {
  return mappedValueFor(selectorOf(AUTHENTICATION_ZONE_WORD), requestUri);
}

function generationCostValueFor(requestUri: string): string {
  return mappedValueFor(selectorOf(GENERATION_COST_ZONE_WORD), requestUri);
}

describe("authentication zone route selection", () => {
  it("throttles brute-force attempts against the login route", () => {
    expect(authenticationValueFor("/api/user/login")).not.toBe("");
  });

  it("throttles bulk account creation on the sign-up route", () => {
    expect(authenticationValueFor("/api/user/sign-up")).not.toBe("");
  });

  it("throttles a sign-in attempt carrying a query string", () => {
    expect(authenticationValueFor("/api/user/login?next=/library")).not.toBe(
      "",
    );
  });

  it("leaves silent token refreshes uncounted", () => {
    expect(authenticationValueFor("/api/user/refresh-token")).toBe("");
  });

  it("leaves logging out uncounted", () => {
    expect(authenticationValueFor("/api/user/logout")).toBe("");
  });

  it("keeps generation traffic out of the sign-in budget", () => {
    for (const route of GENERATION_COST_LIMITED_ROUTES) {
      expect(authenticationValueFor(route)).toBe("");
    }
  });
});

describe("generation-cost zone route selection", () => {
  it("throttles the chat route that spends model tokens", () => {
    expect(generationCostValueFor("/api/content/chat")).not.toBe("");
  });

  it("throttles study-unit generation", () => {
    const route = "/api/content/generate-study-units";

    expect(generationCostValueFor(route)).not.toBe("");
  });

  it("throttles text extraction", () => {
    expect(generationCostValueFor("/api/content/extract-text")).not.toBe("");
  });

  it("throttles file upload", () => {
    expect(generationCostValueFor("/api/content/upload-files")).not.toBe("");
  });

  it("throttles a generation request carrying a query string", () => {
    expect(generationCostValueFor("/api/content/chat?stream=1")).not.toBe("");
  });

  it("keeps sign-in traffic out of the generation budget", () => {
    const signInRoutes = AUTHENTICATION_LIMITED_ROUTES.concat(
      AUTHENTICATION_UNLIMITED_ROUTES,
    );

    for (const route of signInRoutes) {
      expect(generationCostValueFor(route)).toBe("");
    }
  });
});

describe("rate-limit selector maps", () => {
  it("selects on the raw request line, not the rewritten path", () => {
    const selectorMaps = rateLimitSelectorMaps();

    expect(selectorMaps.length).toBe(SELECTOR_MAP_COUNT);

    for (const selectorMap of selectorMaps) {
      expect(selectorMap.sourceVariable).toBe(REQUEST_URI_VARIABLE);
    }
  });

  it("never selects on a variable a location rewrite can change", () => {
    for (const selectorMap of declaredMaps()) {
      expect(selectorMap.sourceVariable).not.toBe(NORMALISED_URI_VARIABLE);
    }
  });

  it("leaves an unlisted route out of every zone it did not name", () => {
    const selectorMaps = rateLimitSelectorMaps();

    expect(selectorMaps.length).toBe(SELECTOR_MAP_COUNT);

    for (const selectorMap of selectorMaps) {
      expect(selectorMap.defaultValue).toBe("");
    }
  });

  it("charges an ordinary read to neither throttled budget", () => {
    for (const route of UNCOUNTED_ROUTES) {
      expect(authenticationValueFor(route)).toBe("");
      expect(generationCostValueFor(route)).toBe("");
    }
  });
});
