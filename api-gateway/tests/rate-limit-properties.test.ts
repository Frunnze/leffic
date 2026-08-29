import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { mappedValueFor } from "./nginx-selector-support";
import {
  AUTHENTICATION_ZONE_WORD,
  CLIENT_ADDRESS_BYTES,
  GENERAL_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
  evaluatedKey,
  requiredApplication,
  requiredZone,
  selectorOf,
} from "./rate-limit-support";

const ZONE_WORDS = [
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
  GENERAL_ZONE_WORD,
];

const LIMITED_ROUTE_MARKERS = [
  "/api/user/",
  "chat",
  "generate-study-units",
  "extract-text",
  "upload-files",
];

function namesLimitedRoute(requestUri: string): boolean {
  return LIMITED_ROUTE_MARKERS.some((marker) => {
    return requestUri.indexOf(marker) !== -1;
  });
}

describe("rate-limit selector properties", () => {
  it("mappedValueFor property invents no value the map never declared", () => {
    const authentication = selectorOf(AUTHENTICATION_ZONE_WORD);
    const declared = authentication.entries.map((entry) => entry.value);

    fc.assert(
      fc.property(fc.string(), (requestUri) => {
        const value = mappedValueFor(authentication, requestUri);

        expect(declared.concat([""])).toContain(value);
      }),
    );
  });

  it("evaluatedKey property spares a route no selector map names", () => {
    fc.assert(
      fc.property(fc.string(), (tail) => {
        const requestUri = `/${tail}`;

        fc.pre(!namesLimitedRoute(requestUri));

        expect(evaluatedKey(AUTHENTICATION_ZONE_WORD, requestUri)).toBe("");
        expect(evaluatedKey(GENERATION_COST_ZONE_WORD, requestUri)).toBe("");
      }),
    );
  });
});

describe("rate-limit zone properties", () => {
  it("requiredZone property gives every zone a rate a client can reach", () => {
    fc.assert(
      fc.property(fc.constantFrom(...ZONE_WORDS), (zoneWord) => {
        expect(requiredZone(zoneWord).ratePerSecond).toBeGreaterThan(0);
      }),
    );
  });

  it("evaluatedKey property charges a counted request to one client", () => {
    fc.assert(
      fc.property(fc.webQueryParameters(), (query) => {
        const requestUri = `/api/user/login?${query}`;

        expect(evaluatedKey(AUTHENTICATION_ZONE_WORD, requestUri)).toBe(
          CLIENT_ADDRESS_BYTES,
        );
      }),
    );
  });

  it("requiredApplication property absorbs a short burst undelayed", () => {
    fc.assert(
      fc.property(fc.constantFrom(...ZONE_WORDS), (zoneWord) => {
        const application = requiredApplication(zoneWord);

        expect(application.burst).not.toBeNull();
        expect(application.burst ?? 0).toBeGreaterThan(0);
        expect(application.hasNoDelay).toBe(true);
      }),
    );
  });

  it("requiredZone property widens a cheaper route's budget", () => {
    const widening = [
      [AUTHENTICATION_ZONE_WORD, GENERATION_COST_ZONE_WORD],
      [GENERATION_COST_ZONE_WORD, GENERAL_ZONE_WORD],
    ] as const;

    fc.assert(
      fc.property(fc.constantFrom(...widening), ([narrower, wider]) => {
        expect(requiredZone(wider).ratePerSecond).toBeGreaterThan(
          requiredZone(narrower).ratePerSecond,
        );
        expect(requiredApplication(wider).burst ?? 0).toBeGreaterThan(
          requiredApplication(narrower).burst ?? 0,
        );
      }),
    );
  });
});
